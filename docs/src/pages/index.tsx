import React, { useEffect } from react;
import useBaseUrl from @docusaurus/useBaseUrl;

export default function HomeRedirect() {
  const target = useBaseUrl(/docs/);
  useEffect(() => {
    if (typeof window !== undefined) {
      window.location.replace(target);
    }
  }, [target]);
  return (
    <main style={{ padding: 2rem }}>
      <h1>Monkey Coder</h1>
      <p>Redirecting to documentation…</p>
      <p><a href={target}>Click here if you are not redirected.</a></p>
    </main>
  );
}