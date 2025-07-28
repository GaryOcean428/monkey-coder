#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class AIReviewConsolidator {
  constructor() {
    this.args = this.parseArgs();
  }

  parseArgs() {
    const args = {};
    const argv = process.argv.slice(2);

    for (let i = 0; i < argv.length; i += 2) {
      const key = argv[i].replace('--', '');
      const value = argv[i + 1];
      args[key] = value;
    }

    return args;
  }

  parseReviewFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      // Try to parse as JSON first
      try {
        return JSON.parse(content);
      } catch (e) {
        // If not JSON, parse as text response from AI
        return this.parseTextResponse(content);
      }
    } catch (error) {
      console.error(`Error reading ${filePath}:`, error);
      return null;
    }
  }

  parseTextResponse(text) {
    // Parse AI text response into structured format
    const review = {
      issues: [],
      suggestions: [],
      score: 0,
    };

    const lines = text.split('\n');
    let currentSection = null;
    let currentIssue = null;

    for (const line of lines) {
      // Detect severity markers
      if (line.match(/critical:|high:|medium:|low:|info:/i)) {
        if (currentIssue) {
          review.issues.push(currentIssue);
        }
        const [severity, ...messageParts] = line.split(':');
        currentIssue = {
          severity: severity.trim().toLowerCase(),
          message: messageParts.join(':').trim(),
          file: null,
          line: null,
        };
      }

      // Detect file references
      const fileMatch = line.match(/file:\s*([^\s,]+)/i);
      if (fileMatch && currentIssue) {
        currentIssue.file = fileMatch[1];
      }

      // Detect line numbers
      const lineMatch = line.match(/line:\s*(\d+)/i);
      if (lineMatch && currentIssue) {
        currentIssue.line = parseInt(lineMatch[1]);
      }

      // Detect scores
      const scoreMatch = line.match(/score:\s*(\d+(?:\.\d+)?)\s*\/\s*10/i);
      if (scoreMatch) {
        review.score = parseFloat(scoreMatch[1]);
      }
    }

    if (currentIssue) {
      review.issues.push(currentIssue);
    }

    return review;
  }

  calculateOverallScore(reviews) {
    const weights = {
      security: 0.4,
      performance: 0.2,
      practices: 0.2,
      railway: 0.2,
    };

    let totalScore = 0;
    let totalWeight = 0;

    for (const [category, review] of Object.entries(reviews)) {
      if (review && review.score !== undefined) {
        const weight = weights[category] || 0.25;
        totalScore += review.score * weight;
        totalWeight += weight;
      }
    }

    return totalWeight > 0 ? (totalScore / totalWeight).toFixed(1) : 0;
  }

  generateLineComments(reviews) {
    const lineComments = [];
    const commentMap = new Map(); // To avoid duplicate comments on same line

    for (const [category, review] of Object.entries(reviews)) {
      if (!review || !review.issues) continue;

      for (const issue of review.issues) {
        if (issue.file && issue.line) {
          const key = `${issue.file}:${issue.line}`;

          if (!commentMap.has(key)) {
            commentMap.set(key, {
              path: issue.file,
              line: issue.line,
              body: `**${category.charAt(0).toUpperCase() + category.slice(1)} Issue** (${issue.severity})\n\n${issue.message}`,
            });
          } else {
            // Append to existing comment
            const existing = commentMap.get(key);
            existing.body += `\n\n**${category.charAt(0).toUpperCase() + category.slice(1)} Issue** (${issue.severity})\n\n${issue.message}`;
          }
        }
      }
    }

    return Array.from(commentMap.values());
  }

  generateSummary(reviews, scores) {
    const totalIssues = Object.values(reviews)
      .filter(r => r && r.issues)
      .reduce((sum, r) => sum + r.issues.length, 0);

    const criticalIssues = Object.values(reviews)
      .filter(r => r && r.issues)
      .reduce(
        (sum, r) =>
          sum + r.issues.filter(i => i.severity === 'critical').length,
        0
      );

    let summary = `The AI review has analyzed your pull request across multiple dimensions:\n\n`;

    if (criticalIssues > 0) {
      summary += `⚠️ **${criticalIssues} critical issues** found that require immediate attention.\n\n`;
    } else if (totalIssues > 0) {
      summary += `📋 **${totalIssues} issues** found, but none are critical.\n\n`;
    } else {
      summary += `✨ **No significant issues found!** Great job!\n\n`;
    }

    // Add category-specific summaries
    if (
      reviews.security &&
      reviews.security.issues &&
      reviews.security.issues.length > 0
    ) {
      summary += `🔒 **Security**: ${reviews.security.issues.length} potential vulnerabilities detected\n`;
    }

    if (
      reviews.performance &&
      reviews.performance.issues &&
      reviews.performance.issues.length > 0
    ) {
      summary += `⚡ **Performance**: ${reviews.performance.issues.length} optimization opportunities found\n`;
    }

    if (
      reviews.practices &&
      reviews.practices.issues &&
      reviews.practices.issues.length > 0
    ) {
      summary += `📚 **Best Practices**: ${reviews.practices.issues.length} code quality improvements suggested\n`;
    }

    return summary;
  }

  generateRecommendation(overallScore, criticalCount) {
    if (criticalCount > 0) {
      return `### 🚫 Recommendation: Address Critical Issues\n\nThis PR contains ${criticalCount} critical issues that must be resolved before merging. Please review the detailed feedback above and make the necessary changes.`;
    } else if (overallScore >= 8) {
      return `### ✅ Recommendation: Ready to Merge\n\nThis PR meets our quality standards with an excellent score. The code is well-written, secure, and follows best practices.`;
    } else if (overallScore >= 6) {
      return `### ⚠️ Recommendation: Minor Improvements Suggested\n\nWhile this PR is generally acceptable, addressing the identified issues would improve code quality. Consider making these changes before merging.`;
    } else {
      return `### 🔧 Recommendation: Significant Improvements Needed\n\nThis PR requires substantial improvements before it can be merged. Please address the identified issues and request a new review.`;
    }
  }

  consolidate() {
    const reviews = {
      security: this.parseReviewFile(this.args.security),
      performance: this.parseReviewFile(this.args.performance),
      practices: this.parseReviewFile(this.args.practices),
    };

    // Calculate Railway compliance from practices review
    const railwayScore =
      reviews.practices && reviews.practices.issues
        ? Math.max(
            0,
            10 -
              reviews.practices.issues.filter(
                i =>
                  i.message.toLowerCase().includes('railway') ||
                  i.message.toLowerCase().includes('port') ||
                  i.message.toLowerCase().includes('cors')
              ).length
          )
        : 10;

    const scores = {
      security: reviews.security ? reviews.security.score || 7 : 7,
      performance: reviews.performance ? reviews.performance.score || 7 : 7,
      practices: reviews.practices ? reviews.practices.score || 7 : 7,
      railway: railwayScore,
      overall: 0,
    };

    scores.overall = this.calculateOverallScore(reviews);

    const criticalCount = Object.values(reviews)
      .filter(r => r && r.issues)
      .reduce(
        (sum, r) =>
          sum + r.issues.filter(i => i.severity === 'critical').length,
        0
      );

    const consolidatedReview = {
      timestamp: new Date().toISOString(),
      scores,
      summary: this.generateSummary(reviews, scores),
      recommendation: this.generateRecommendation(
        scores.overall,
        criticalCount
      ),
      lineComments: this.generateLineComments(reviews),
      reviews,
      metadata: {
        totalIssues: Object.values(reviews)
          .filter(r => r && r.issues)
          .reduce((sum, r) => sum + r.issues.length, 0),
        criticalIssues: criticalCount,
        warningIssues: Object.values(reviews)
          .filter(r => r && r.issues)
          .reduce(
            (sum, r) =>
              sum + r.issues.filter(i => i.severity === 'warning').length,
            0
          ),
      },
    };

    // Write output
    if (this.args.output) {
      fs.writeFileSync(
        this.args.output,
        JSON.stringify(consolidatedReview, null, 2)
      );
    } else {
      console.log(JSON.stringify(consolidatedReview, null, 2));
    }
  }
}

// Run consolidator
const consolidator = new AIReviewConsolidator();
consolidator.consolidate();
