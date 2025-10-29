// Performance logging utility
export class PerformanceLogger {
  private static marks: Map<string, number> = new Map();

  static start(label: string): void {
    if (typeof window !== 'undefined') {
      performance.mark(`start-${label}`);
      console.time(`⏱️ ${label}`);
    }
    this.marks.set(label, Date.now());
  }

  static end(label: string): void {
    const startTime = this.marks.get(label);
    if (startTime) {
      const duration = Date.now() - startTime;
      if (typeof window !== 'undefined') {
        performance.mark(`end-${label}`);
        performance.measure(label, `start-${label}`, `end-${label}`);
        const measure = performance.getEntriesByName(label)[0];
        console.timeEnd(`⏱️ ${label}`);
        console.log(`📊 ${label}: ${duration}ms (Performance API: ${measure?.duration.toFixed(2)}ms)`);
      } else {
        console.log(`📊 ${label}: ${duration}ms`);
      }
      this.marks.delete(label);
    }
  }

  static log(label: string, message: string, data?: any): void {
    console.log(`📝 [${label}] ${message}`, data || '');
  }

  static error(label: string, message: string, error?: any): void {
    console.error(`❌ [${label}] ${message}`, error || '');
  }

  static warn(label: string, message: string): void {
    console.warn(`⚠️ [${label}] ${message}`);
  }
}
