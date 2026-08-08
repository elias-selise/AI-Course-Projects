import '@testing-library/jest-dom';

// Mock EventSource globally if not available in jsdom
if (typeof window !== 'undefined' && !window.EventSource) {
  class MockEventSource {
    url: string;
    onopen: ((event: Event) => void) | null = null;
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: Event) => void) | null = null;
    readyState: number = 0;
    
    constructor(url: string) {
      this.url = url;
    }
    
    close() {
      this.readyState = 2;
    }
  }

  // @ts-ignore
  window.EventSource = MockEventSource;
}
