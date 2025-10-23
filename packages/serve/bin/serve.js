#!/usr/bin/env node

const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const process = require('node:process');
const url = require('node:url');

const METHODS = new Set(['GET', 'HEAD']);

function parseArgs(argv) {
  const result = {
    root: '.',
    single: false,
    listen: process.env.PORT ? Number.parseInt(process.env.PORT, 10) : 3000,
    host: '0.0.0.0',
    configPath: null,
  };

  const args = [...argv];
  while (args.length > 0) {
    const token = args.shift();
    if (token === '-s' || token === '--single') {
      result.single = true;
      continue;
    }
    if (token === '-l' || token === '--listen') {
      const value = args.shift();
      if (!value) {
        throw new Error('Missing value for --listen option');
      }
      const listenTarget = value.trim();
      if (listenTarget.includes(':')) {
        const parts = listenTarget.split(':');
        const portPart = parts.pop();
        const hostPart = parts.join(':') || result.host;
        const parsedPort = Number.parseInt(portPart, 10);
        if (Number.isNaN(parsedPort)) {
          throw new Error(`Invalid port: ${listenTarget}`);
        }
        result.host = hostPart || result.host;
        result.listen = parsedPort;
      } else {
        const parsedPort = Number.parseInt(listenTarget, 10);
        if (Number.isNaN(parsedPort)) {
          throw new Error(`Invalid port: ${listenTarget}`);
        }
        result.listen = parsedPort;
      }
      continue;
    }
    if (token === '-H' || token === '--hostname') {
      const value = args.shift();
      if (!value) {
        throw new Error('Missing value for --hostname option');
      }
      result.host = value;
      continue;
    }
    if (token === '-c' || token === '--config') {
      const value = args.shift();
      if (!value) {
        throw new Error('Missing value for --config option');
      }
      result.configPath = value;
      continue;
    }
    if (token.startsWith('-')) {
      throw new Error(`Unknown option: ${token}`);
    }
    if (result.root !== '.') {
      throw new Error(`Unexpected extra argument: ${token}`);
    }
    result.root = token;
  }

  return result;
}

function loadConfig(configPath) {
  if (!configPath) {
    return {};
  }
  const absolutePath = path.resolve(process.cwd(), configPath);
  try {
    const raw = fs.readFileSync(absolutePath, 'utf8');
    const config = JSON.parse(raw);
    if (config.public) {
      config.public = path.resolve(path.dirname(absolutePath), config.public);
    }
    return config;
  } catch (error) {
    throw new Error(`Failed to read config at ${configPath}: ${error.message}`);
  }
}

function toRegex(pattern) {
  if (!pattern || pattern === '/') {
    return /^\/.*$/;
  }
  const normalized = pattern.startsWith('/') ? pattern : `/${pattern}`;
  const escaped = normalized.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
  const regexBody = escaped
    .replace(/\\\*\\\*/g, '.*')
    .replace(/\\\*/g, '[^/]*');
  return new RegExp(`^${regexBody}$`);
}

function createPatternMatcher(rules) {
  const compiled = rules
    .filter((rule) => rule && rule.source)
    .map((rule) => ({ ...rule, regex: toRegex(rule.source) }));
  return (pathname) => {
    for (const rule of compiled) {
      if (rule.regex.test(pathname)) {
        return rule;
      }
    }
    return null;
  };
}

function createHeaderMatcher(headerRules) {
  const compiled = headerRules
    .filter((rule) => rule && rule.source && Array.isArray(rule.headers))
    .map((rule) => ({ ...rule, regex: toRegex(rule.source) }));
  return (pathname, res) => {
    for (const rule of compiled) {
      if (!rule.regex.test(pathname)) {
        continue;
      }
      for (const header of rule.headers) {
        if (header && header.key && header.value !== undefined) {
          res.setHeader(header.key, header.value);
        }
      }
    }
  };
}

function isSubPath(rootPrefix, candidate) {
  return candidate === rootPrefix.slice(0, -1) || candidate.startsWith(rootPrefix);
}

function createFileResolver(options) {
  const rootDir = path.resolve(process.cwd(), options.root);
  const rootPrefix = rootDir.endsWith(path.sep) ? rootDir : `${rootDir}${path.sep}`;
  const fallbackPath = options.single ? resolveWithinRoot(rootDir, rootPrefix, 'index.html') : null;
  const trailingSlash = options.trailingSlash ?? false;
  const cleanUrls = options.cleanUrls ?? false;

  function resolveWithinRoot(base, prefix, relativePath) {
    const cleanRelative = relativePath.replace(/^\/+/, '');
    const resolved = path.resolve(base, cleanRelative);
    if (!isSubPath(prefix, resolved)) {
      return null;
    }
    return resolved;
  }

  async function tryFile(resolvedPath) {
    if (!resolvedPath) {
      return null;
    }
    try {
      const stats = await fs.promises.stat(resolvedPath);
      if (stats.isFile()) {
        return { type: 'file', path: resolvedPath, stats };
      }
      if (stats.isDirectory()) {
        return { type: 'dir', path: resolvedPath, stats };
      }
    } catch (error) {
      if (error.code !== 'ENOENT' && error.code !== 'ENOTDIR') {
        throw error;
      }
    }
    return null;
  }

  async function resolvePath(pathname) {
    const sanitized = pathname === '' ? '/' : pathname;
    const relative = sanitized.replace(/^\/+/, '');

    const direct = await tryFile(resolveWithinRoot(rootDir, rootPrefix, relative));
    if (direct && direct.type === 'file') {
      return { filePath: direct.path, stats: direct.stats };
    }

    if (direct && direct.type === 'dir') {
      if (trailingSlash && !sanitized.endsWith('/')) {
        return { redirectTo: `${sanitized}/` };
      }
      const indexPath = resolveWithinRoot(rootDir, rootPrefix, path.join(relative, 'index.html'));
      const indexFile = await tryFile(indexPath);
      if (indexFile && indexFile.type === 'file') {
        return { filePath: indexFile.path, stats: indexFile.stats };
      }
    }

    if (cleanUrls && !path.extname(relative)) {
      const htmlCandidate = await tryFile(resolveWithinRoot(rootDir, rootPrefix, `${relative}.html`));
      if (htmlCandidate && htmlCandidate.type === 'file') {
        return { filePath: htmlCandidate.path, stats: htmlCandidate.stats };
      }
      const indexCandidate = await tryFile(resolveWithinRoot(rootDir, rootPrefix, path.join(relative, 'index.html')));
      if (indexCandidate && indexCandidate.type === 'file') {
        return { filePath: indexCandidate.path, stats: indexCandidate.stats };
      }
    }

    if (options.single && fallbackPath) {
      const fallbackFile = await tryFile(fallbackPath);
      if (fallbackFile && fallbackFile.type === 'file') {
        return { filePath: fallbackFile.path, stats: fallbackFile.stats };
      }
    }

    return null;
  }

  return resolvePath;
}

function lookupContentType(filePath) {
  const extension = path.extname(filePath).toLowerCase();
  switch (extension) {
    case '.html':
    case '.htm':
      return 'text/html; charset=utf-8';
    case '.js':
      return 'text/javascript; charset=utf-8';
    case '.mjs':
      return 'text/javascript; charset=utf-8';
    case '.cjs':
      return 'text/javascript; charset=utf-8';
    case '.css':
      return 'text/css; charset=utf-8';
    case '.json':
      return 'application/json; charset=utf-8';
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.gif':
      return 'image/gif';
    case '.svg':
      return 'image/svg+xml';
    case '.ico':
      return 'image/x-icon';
    case '.txt':
      return 'text/plain; charset=utf-8';
    case '.webp':
      return 'image/webp';
    case '.wasm':
      return 'application/wasm';
    case '.map':
      return 'application/json; charset=utf-8';
    case '.xml':
      return 'application/xml; charset=utf-8';
    case '.woff':
      return 'font/woff';
    case '.woff2':
      return 'font/woff2';
    case '.ttf':
      return 'font/ttf';
    default:
      return 'application/octet-stream';
  }
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }

  const config = loadConfig(options.configPath);
  const publicRoot = config.public ? config.public : path.resolve(process.cwd(), options.root);
  const rewrites = Array.isArray(config.rewrites) ? config.rewrites : [];
  const headers = Array.isArray(config.headers) ? config.headers : [];
  const matcher = createPatternMatcher(rewrites);
  const hasCatchAllRewrite = rewrites.some(
    (rule) => rule && rule.source === '**' && typeof rule.destination === 'string'
  );
  const applyHeaders = createHeaderMatcher(headers);

  const resolveFile = createFileResolver({
    root: publicRoot,
    single: options.single || hasCatchAllRewrite,
    trailingSlash: config.trailingSlash,
    cleanUrls: config.cleanUrls,
  });

  const server = http.createServer((req, res) => {
    if (!METHODS.has(req.method || '')) {
      res.statusCode = 405;
      res.setHeader('Allow', 'GET, HEAD');
      res.end('Method Not Allowed');
      return;
    }

    const parsedUrl = url.parse(req.url || '/');
    let pathname;
    try {
      pathname = decodeURIComponent(parsedUrl.pathname || '/');
    } catch (error) {
      res.statusCode = 400;
      res.end('Bad Request');
      return;
    }
    if (!pathname.startsWith('/')) {
      pathname = `/${pathname}`;
    }

    const rewriteRule = matcher(pathname);
    const rewriteDestination =
      rewriteRule && rewriteRule.destination
        ? rewriteRule.destination.startsWith('/')
          ? rewriteRule.destination
          : `/${rewriteRule.destination}`
        : null;

    const sendNotFound = () => {
      res.statusCode = 404;
      res.end('Not Found');
    };

    const sendResult = (result, servedPath) => {
      if (result.redirectTo) {
        res.statusCode = 301;
        res.setHeader('Location', result.redirectTo);
        res.end();
        return;
      }

      res.statusCode = 200;
      const contentType = lookupContentType(result.filePath);
      res.setHeader('Content-Type', contentType);
      res.setHeader('Content-Length', result.stats.size);
      res.setHeader('Last-Modified', result.stats.mtime.toUTCString());
      applyHeaders(servedPath, res);

      if (req.method === 'HEAD') {
        res.end();
        return;
      }

      const stream = fs.createReadStream(result.filePath);
      stream.on('error', (error) => {
        console.error('Failed to read file', error);
        if (!res.headersSent) {
          res.statusCode = 500;
        }
        res.end('Internal Server Error');
      });
      stream.pipe(res);
    };

    resolveFile(pathname)
      .then((result) => {
        if (result) {
          sendResult(result, pathname);
          return;
        }

        if (!rewriteDestination || rewriteDestination === pathname) {
          sendNotFound();
          return;
        }

        resolveFile(rewriteDestination)
          .then((rewriteResult) => {
            if (rewriteResult) {
              sendResult(rewriteResult, rewriteDestination);
            } else {
              sendNotFound();
            }
          })
          .catch((error) => {
            console.error('Error while handling rewrite', error);
            if (!res.headersSent) {
              res.statusCode = 500;
              res.setHeader('Content-Type', 'text/plain; charset=utf-8');
            }
            res.end('Internal Server Error');
          });
      })
      .catch((error) => {
        console.error('Error while handling request', error);
        if (!res.headersSent) {
          res.statusCode = 500;
          res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        }
        res.end('Internal Server Error');
      });
  });

  server.on('clientError', (err, socket) => {
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
  });

  server.listen(options.listen, options.host, () => {
    const address = server.address();
    if (address && typeof address === 'object') {
      console.log(`Serving ${publicRoot} at http://${address.address}:${address.port}`);
    } else {
      console.log(`Serving ${publicRoot}`);
    }
  });
}

main();
