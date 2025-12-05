import { v4 as uuidv4 } from 'uuid';

export interface LogContext {
  [key: string]: any;
}

/**
 * 简单的 UUID 生成器 (如果不想引入 uuid 库)
 */
function generateTraceId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

class Logger {
  private context: LogContext = {};
  private traceId: string | null = null;

  constructor(context: LogContext = {}) {
    this.context = context;
  }

  /**
   * 创建带有新上下文的子 Logger
   */
  withContext(context: LogContext): Logger {
    const newLogger = new Logger({ ...this.context, ...context });
    newLogger.traceId = this.traceId;
    return newLogger;
  }

  /**
   * 开始一个新的 Trace
   */
  startTrace(traceId?: string): Logger {
    const newLogger = new Logger({ ...this.context });
    newLogger.traceId = traceId || generateTraceId();
    return newLogger;
  }

  getTraceId(): string | null {
    return this.traceId;
  }

  private log(level: 'info' | 'warn' | 'error' | 'debug', message: string, meta?: any) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      ts: timestamp,
      lvl: level,
      msg: message,
      trace_id: this.traceId,
      ...this.context,
      ...meta,
    };
    
    // 开发环境：彩色输出 + 对象展开
    if (import.meta.env.DEV) {
        const style = {
            info: 'color: #3b82f6; font-weight: bold',
            warn: 'color: #f59e0b; font-weight: bold',
            error: 'color: #ef4444; font-weight: bold',
            debug: 'color: #6b7280; font-weight: bold',
        }[level];

        console.groupCollapsed(`%c[${level.toUpperCase()}] ${message}`, style);
        if (this.traceId) console.log('%cTrace ID:', 'color: #8b5cf6', this.traceId);
        if (Object.keys(this.context).length > 0) console.log('Context:', this.context);
        if (meta) console.log('Meta:', meta);
        console.groupEnd();
    } else {
        // 生产环境：单行 JSON
        console.log(JSON.stringify(logEntry));
    }
  }

  info(message: string, meta?: any) { this.log('info', message, meta); }
  error(message: string, meta?: any) { this.log('error', message, meta); }
  warn(message: string, meta?: any) { this.log('warn', message, meta); }
  debug(message: string, meta?: any) { this.log('debug', message, meta); }
}

export const logger = new Logger();

