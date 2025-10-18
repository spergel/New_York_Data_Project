declare module 'page-flip' {
  export interface PageFlipOptions {
    width?: number;
    height?: number;
    size?: 'fixed' | 'stretch';
    minWidth?: number;
    maxWidth?: number;
    minHeight?: number;
    maxHeight?: number;
    showCover?: boolean;
    usePortrait?: boolean;
    maxShadowOpacity?: number;
    mobileScrollSupport?: boolean;
    flippingTime?: number;
  }

  export interface PageFlipEvent {
    data: number;
  }

  export default class PageFlip {
    constructor(element: HTMLElement, options?: PageFlipOptions);
    
    loadFromHTML(pages: NodeListOf<Element>): void;
    flip(pageNum: number): void;
    flipNext(): void;
    flipPrev(): void;
    getPageCount(): number;
    getCurrentPageIndex(): number;
    destroy(): void;
    
    on(event: 'flip' | 'changeState', callback: (e: PageFlipEvent) => void): void;
  }
}

