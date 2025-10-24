// Decode HTML entities
export function decodeHtmlEntities(html: string): string {
  if (!html) return '';
  
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  return tempDiv.textContent || tempDiv.innerText || html;
}

// Simple HTML sanitizer for safe rendering
export function sanitizeHtml(html: string): string {
  if (!html) return '';

  // First decode HTML entities (like &lt; to <, &gt; to >, etc.)
  const decodedHtml = decodeHtmlEntities(html);

  // Allow more HTML tags for rich content in event descriptions
  const allowedTags = [
    'strong', 'em', 'b', 'i', 'u', 'br', 'p', 'a', 'span', 
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'ul', 'ol', 'li',
    'blockquote', 'code', 'pre'
  ];
  const allowedAttributes = ['href', 'target', 'title', 'class', 'id'];

  // Create a new temporary div to parse the decoded HTML
  const sanitizeDiv = document.createElement('div');
  sanitizeDiv.innerHTML = decodedHtml;

  // Remove dangerous tags
  const dangerousTags = ['script', 'object', 'embed', 'iframe', 'form', 'input', 'button', 'style'];
  dangerousTags.forEach(tag => {
    const elements = sanitizeDiv.querySelectorAll(tag);
    elements.forEach(el => el.remove());
  });

  // Remove dangerous attributes
  const allElements = sanitizeDiv.querySelectorAll('*');
  allElements.forEach(el => {
    const attributes = Array.from(el.attributes);
    attributes.forEach(attr => {
      if (!allowedAttributes.includes(attr.name)) {
        el.removeAttribute(attr.name);
      }
    });
  });

  // Clean up href attributes to only allow http/https and mailto
  const links = sanitizeDiv.querySelectorAll('a[href]');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href && !href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('mailto:')) {
      link.removeAttribute('href');
    }
  });

  return sanitizeDiv.innerHTML;
}

// Safe text rendering for different content types
export function sanitizeText(text: string, allowHtml: boolean = false): string {
  if (!text) return '';

  if (allowHtml) {
    return sanitizeHtml(text);
  }

  // For plain text, escape HTML entities
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

// Sanitize title text (minimal HTML allowed)
export function sanitizeTitle(text: string): string {
  if (!text) return '';

  // Allow only basic formatting in titles
  const allowedTags = ['strong', 'em', 'b', 'i'];
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = text;

  // Remove all tags except allowed ones
  const allElements = tempDiv.querySelectorAll('*');
  allElements.forEach(el => {
    if (!allowedTags.includes(el.tagName.toLowerCase())) {
      // Replace tag with its text content
      const textNode = document.createTextNode(el.textContent || '');
      el.parentNode?.replaceChild(textNode, el);
    } else {
      // Remove all attributes from allowed tags
      Array.from(el.attributes).forEach(attr => {
        el.removeAttribute(attr.name);
      });
    }
  });

  return tempDiv.innerHTML;
}

// Escape text for safe use in JavaScript strings (for onclick handlers, etc.)
export function escapeForJS(text: string): string {
  if (!text) return '';
  return text
    .replace(/\\/g, '\\\\')  // Escape backslashes
    .replace(/'/g, '\\\'')   // Escape single quotes
    .replace(/"/g, '\\"')    // Escape double quotes
    .replace(/\n/g, '\\n')   // Escape newlines
    .replace(/\r/g, '\\r')   // Escape carriage returns
    .replace(/\t/g, '\\t');  // Escape tabs
}

// Alternative: Use a more robust approach with DOMPurify if available
export function sanitizeHtmlWithDOMPurify(html: string): string {
  // This would require installing dompurify: npm install dompurify @types/dompurify
  // For now, we'll use the simple sanitizer above
  return sanitizeHtml(html);
}

