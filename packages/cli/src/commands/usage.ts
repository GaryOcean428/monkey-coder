/**
 * Usage and billing commands for Monkey Coder CLI
 * Shows usage statistics, costs, and billing management
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { requireAuth } from './auth.js';

interface UsageData {
  period: {
    start_date: string;
    end_date: string;
  };
  summary: {
    total_cost: number;
    total_tokens: number;
    total_requests: number;
    credits_remaining: number;
  };
  by_model: Array<{
    provider: string;
    model: string;
    requests: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    cost: number;
  }>;
  by_agent: Array<{
    agent_name: string;
    requests: number;
    total_cost: number;
    avg_cost_per_request: number;
  }>;
  daily_usage: Array<{
    date: string;
    requests: number;
    tokens: number;
    cost: number;
  }>;
}

interface BillingPortalResponse {
  portal_url: string;
  session_id: string;
  expires_at: string;
}

export function createUsageCommand(config: ConfigManager): Command {
  const usage = new Command('usage')
    .description('View usage statistics and costs');

  // Default usage command - show current month
  usage
    .action(async () => {
      await requireAuth(config);
      
      try {
        const spinner = ora('Fetching usage data...').start();
        
        const client = new MonkeyCoderAPIClient(config.getBaseUrl(), config.getApiKey()!);
        
        // Get current month date range
        const now = new Date();
        const startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        const endDate = now.toISOString().split('T')[0];
        
        const usageData = await client.getUsage({
          startDate,
          endDate,
          granularity: 'daily',
        }) as UsageData;
        
        spinner.stop();
        
        // Display usage summary
        console.log(chalk.cyan('\n📊 Usage Summary'));
        console.log(chalk.gray(`Period: ${usageData.period.start_date} to ${usageData.period.end_date}`));
        console.log();
        
        console.log(chalk.blue('Summary:'));
        console.log(`  Total Requests: ${usageData.summary.total_requests}`);
        console.log(`  Total Tokens: ${usageData.summary.total_tokens.toLocaleString()}`);
        console.log(`  Total Cost: ${chalk.yellow(`$${(usageData.summary.total_cost / 100).toFixed(2)}`)}`);
        console.log(`  Credits Remaining: ${chalk.green(`$${(usageData.summary.credits_remaining / 100).toFixed(2)}`)}`);
        
        // Display by model
        if (usageData.by_model.length > 0) {
          console.log(chalk.blue('\nUsage by Model:'));
          const modelTable = usageData.by_model
            .sort((a, b) => b.cost - a.cost)
            .slice(0, 5);
          
          for (const model of modelTable) {
            console.log(`  ${model.provider}/${model.model}:`);
            console.log(`    Requests: ${model.requests}`);
            console.log(`    Tokens: ${model.total_tokens.toLocaleString()}`);
            console.log(`    Cost: ${chalk.yellow(`$${(model.cost / 100).toFixed(2)}`)}`);
          }
        }
        
        // Display by agent
        if (usageData.by_agent && usageData.by_agent.length > 0) {
          console.log(chalk.blue('\nUsage by Agent:'));
          const agentTable = usageData.by_agent
            .sort((a, b) => b.total_cost - a.total_cost)
            .slice(0, 5);
          
          for (const agent of agentTable) {
            console.log(`  ${agent.agent_name}:`);
            console.log(`    Requests: ${agent.requests}`);
            console.log(`    Total Cost: ${chalk.yellow(`$${(agent.total_cost / 100).toFixed(2)}`)}`);
            console.log(`    Avg Cost/Request: ${chalk.yellow(`$${(agent.avg_cost_per_request / 100).toFixed(3)}`)}`);
          }
        }
        
        // Display daily trend (last 7 days)
        if (usageData.daily_usage && usageData.daily_usage.length > 0) {
          console.log(chalk.blue('\nLast 7 Days:'));
          const last7Days = usageData.daily_usage.slice(-7);
          
          for (const day of last7Days) {
            const date = new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            const costBar = '█'.repeat(Math.round(day.cost / 10));
            console.log(`  ${date}: ${costBar} ${chalk.yellow(`$${(day.cost / 100).toFixed(2)}`)} (${day.requests} requests)`);
          }
        }
        
        console.log(chalk.gray('\nFor detailed billing information, run "monkey billing portal"'));
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to fetch usage data'));
        process.exit(1);
      }
    });

  // Usage for specific date range
  usage
    .command('range <start> <end>')
    .description('View usage for a specific date range')
    .action(async (start: string, end: string) => {
      await requireAuth(config);
      
      try {
        const spinner = ora('Fetching usage data...').start();
        
        const client = new MonkeyCoderAPIClient(config.getBaseUrl(), config.getApiKey()!);
        
        const usageData = await client.getUsage({
          startDate: start,
          endDate: end,
          granularity: 'daily',
        }) as UsageData;
        
        spinner.stop();
        
        // Display usage (similar to above but for custom range)
        console.log(chalk.cyan('\n📊 Usage Summary'));
        console.log(chalk.gray(`Period: ${usageData.period.start_date} to ${usageData.period.end_date}`));
        // ... rest of the display logic
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to fetch usage data'));
        process.exit(1);
      }
    });

  return usage;
}

export function createBillingCommand(config: ConfigManager): Command {
  const billing = new Command('billing')
    .description('Billing and payment management');

  // Billing portal command
  billing
    .command('portal')
    .description('Open billing portal in browser')
    .action(async () => {
      await requireAuth(config);
      
      try {
        const spinner = ora('Creating billing portal session...').start();
        
        const client = new MonkeyCoderAPIClient(config.getBaseUrl(), config.getApiKey()!);
        
        // Create billing portal session
        const response = await client.createBillingPortalSession({
          return_url: 'https://app.monkeycoder.dev/billing',
        }) as BillingPortalResponse;
        
        spinner.succeed('Billing portal session created');
        
        console.log(chalk.green('\n✓ Billing portal URL:'));
        console.log(chalk.blue(response.portal_url));
        console.log(chalk.gray('\nThis link will expire in 1 hour.'));
        
        // Try to open in browser
        try {
          const open = await import('open');
          await open.default(response.portal_url);
          console.log(chalk.gray('Opening in your default browser...'));
        } catch {
          console.log(chalk.gray('Please copy and paste the URL into your browser.'));
        }
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to create billing portal session'));
        process.exit(1);
      }
    });

  // Buy credits command
  billing
    .command('credits <amount>')
    .description('Purchase additional credits')
    .action(async (amount: string) => {
      await requireAuth(config);
      
      try {
        const creditAmount = parseFloat(amount);
        if (isNaN(creditAmount) || creditAmount < 5) {
          console.error(chalk.red('Invalid amount. Minimum purchase is $5.00'));
          process.exit(1);
        }
        
        const spinner = ora('Creating payment session...').start();
        
        const client = new MonkeyCoderAPIClient(config.getBaseUrl(), config.getApiKey()!);
        
        // Create payment session for credits
        const response = await client.createPaymentSession({
          amount: Math.round(creditAmount * 100), // Convert to cents
          description: `${creditAmount} credits for Monkey Coder`,
          success_url: 'https://app.monkeycoder.dev/billing/success',
          cancel_url: 'https://app.monkeycoder.dev/billing/cancel',
        }) as { payment_url: string };
        
        spinner.succeed('Payment session created');
        
        console.log(chalk.green(`\n✓ Purchase $${creditAmount.toFixed(2)} in credits`));
        console.log(chalk.blue('Payment URL:'), response.payment_url);
        
        // Try to open in browser
        try {
          const open = await import('open');
          await open.default(response.payment_url);
          console.log(chalk.gray('Opening in your default browser...'));
        } catch {
          console.log(chalk.gray('Please copy and paste the URL into your browser.'));
        }
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to create payment session'));
        process.exit(1);
      }
    });

  return billing;
}

// Add methods to API client
declare module '../api-client.js' {
  interface MonkeyCoderAPIClient {
    createBillingPortalSession(data: { return_url: string }): Promise<any>;
    createPaymentSession(data: {
      amount: number;
      description: string;
      success_url: string;
      cancel_url: string;
    }): Promise<any>;
  }
}
