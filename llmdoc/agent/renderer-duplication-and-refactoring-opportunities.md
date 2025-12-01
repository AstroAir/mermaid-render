# Renderer Duplication and Refactoring Opportunities

## Evidence

### Code Section: SVGRenderer Initialization Pattern

**File:** `diagramaid/renderers/svg_renderer.py`
**Lines:** 37-91
**Purpose:** Initialize SVG renderer with configuration, session, caching, and performance metrics

```python
def __init__(
    self,
    server_url: str = "https://mermaid.ink",
    timeout: float = 30.0,
    use_local: bool = True,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    cache_enabled: bool = True,
    cache_dir: Optional[str] = None,
    cache_ttl: int = 3600,
) -> None:
    self.server_url = server_url.rstrip("/")
    self.timeout = timeout
    self.use_local = use_local
    self.max_retries = max_retries
    self.backoff_factor = backoff_factor
    self.cache_enabled = cache_enabled
    self.cache_ttl = cache_ttl

    # Set up caching
    if cache_dir:
        self.cache_dir = Path(cache_dir)
    else:
        self.cache_dir = Path.home() / ".diagramaid_cache"

    if self.cache_enabled:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging
    self.logger = logging.getLogger(__name__)

    # Create a session with retry strategy
    self._session = self._create_session()

    # Performance metrics
    self._metrics: Dict[str, Any] = {
        "cache_hits": 0,
        "cache_misses": 0,
        "render_times": [],
        "total_requests": 0,
    }
```

**Key Details:**
- Contains manual cache directory setup
- Manual performance metrics initialization
- Session creation logic
- URL normalization (rstrip("/"))

### Code Section: PNGRenderer Initialization Pattern

**File:** `diagramaid/renderers/png_renderer.py`
**Lines:** 24-43
**Purpose:** Initialize PNG renderer with basic configuration

```python
def __init__(
    self,
    server_url: str = "https://mermaid.ink",
    timeout: float = 30.0,
    width: int = 800,
    height: int = 600,
) -> None:
    self.server_url = server_url.rstrip("/")
    self.timeout = timeout
    self.default_width = width
    self.default_height = height
```

**Key Details:**
- Same server_url pattern with rstrip("/")
- No caching implementation despite similar use case
- No logging setup
- No session management despite making network requests

### Code Section: PDFRenderer Initialization Pattern

**File:** `diagramaid/renderers/pdf_renderer.py`
**Lines:** 22-38
**Purpose:** Initialize PDF renderer with SVGRenderer dependency

```python
def __init__(
    self,
    svg_renderer: Optional[SVGRenderer] = None,
    page_size: str = "A4",
    orientation: str = "portrait",
) -> None:
    self.svg_renderer = svg_renderer or SVGRenderer()
    self.page_size = page_size
    self.orientation = orientation
```

**Key Details:**
- Depends on SVGRenderer instance
- No direct server or session configuration
- No caching (relies on SVGRenderer's cache)

### Code Section: SVGRenderer HTTP Session Creation

**File:** `diagramaid/renderers/svg_renderer.py`
**Lines:** 92-111
**Purpose:** Create HTTP session with default headers

```python
def _create_session(self) -> requests.Session:
    session = requests.Session()

    # Set default headers
    session.headers.update(
        {
            "User-Agent": "diagramaid/1.0.0",
            "Accept": "image/svg+xml,text/plain,*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    )

    return session
```

**Key Details:**
- Header configuration is renderer-specific
- Version hardcoded in User-Agent string
- No retry logic integrated into session

### Code Section: PNGRenderer Direct HTTP Request

**File:** `diagramaid/renderers/png_renderer.py`
**Lines:** 99-101
**Purpose:** Make HTTP request without session reuse

```python
response = requests.get(url, params=params, timeout=self.timeout)
response.raise_for_status()
```

**Key Details:**
- Uses requests.get directly (no session reuse)
- No connection pooling
- No custom headers
- Same timeout pattern as SVGRenderer

### Code Section: SVGRenderer Cache Key Generation

**File:** `diagramaid/renderers/svg_renderer.py`
**Lines:** 113-126
**Purpose:** Generate cache key from parameters

```python
def _generate_cache_key(
    self, mermaid_code: str, theme: Optional[str], config: Optional[Dict[str, Any]]
) -> str:
    # Create a hash of the input parameters
    cache_data = {
        "code": mermaid_code,
        "theme": theme,
        "config": config or {},
        "server_url": self.server_url,
    }

    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.sha256(cache_string.encode()).hexdigest()
```

**Key Details:**
- Manual implementation of cache key generation
- JSON serialization with sorted keys
- SHA256 hashing

### Code Section: CacheKey Class Implementation

**File:** `diagramaid/cache/cache_manager.py`
**Lines:** 88-174
**Purpose:** Generate cache keys with type safety and structure

```python
class CacheKey:
    def __init__(
        self,
        content_hash: str,
        key_type: CacheKeyType,
        format: str = "svg",
        theme: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        version: str = "1.0"
    ):
        self.content_hash = content_hash
        self.key_type = key_type
        # ... more fields
        self.key = self._generate_key()

    def _generate_key(self) -> str:
        key_data = {
            "hash": self.content_hash,
            "type": self.key_type.value,
            "format": self.format,
            "theme": self.theme,
            "options": self.options,
            "version": self.version,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
```

**Key Details:**
- Structured cache key with type information
- Enum-based key types
- Shorter hash (16 chars) for key generation
- Comparable and hashable

### Code Section: SVGRenderer Theme Support

**File:** `diagramaid/renderers/svg_renderer.py`
**Lines:** 1318-1385
**Purpose:** Theme information and validation

```python
def get_supported_themes(self) -> Dict[str, Dict[str, Any]]:
    return {
        "default": {
            "name": "Default",
            "description": "Standard Mermaid theme with blue and gray colors",
            "colors": {
                "primaryColor": "#0066cc",
                "primaryTextColor": "#ffffff",
                # ... more colors
            },
        },
        "dark": { ... },
        "forest": { ... },
        # ... more themes
    }

def get_theme_names(self) -> list[str]:
    return list(self.get_supported_themes().keys())

def validate_theme(self, theme: str) -> bool:
    return theme in self.get_theme_names()
```

**Key Details:**
- Theme definitions duplicated in renderer
- Same themes should be centralized

### Code Section: PNGRenderer Theme Support

**File:** `diagramaid/renderers/png_renderer.py`
**Lines:** 143-149
**Purpose:** Theme list with simpler implementation

```python
def get_supported_themes(self) -> list[str]:
    return ["default", "dark", "forest", "neutral", "base"]

def validate_theme(self, theme: str) -> bool:
    return theme in self.get_supported_themes()
```

**Key Details:**
- Returns list instead of dict
- Same theme names as SVGRenderer but less information
- Inconsistent return type

### Code Section: PDFRenderer Theme Delegation

**File:** `diagramaid/renderers/pdf_renderer.py`
**Lines:** 232-239
**Purpose:** Delegate theme operations to SVGRenderer

```python
def get_supported_themes(self) -> list[str]:
    themes = self.svg_renderer.get_supported_themes()
    return list(themes.keys()) if isinstance(themes, dict) else themes

def validate_theme(self, theme: str) -> bool:
    return self.svg_renderer.validate_theme(theme)
```

**Key Details:**
- Type checking to handle dict vs list inconsistency
- Proper delegation pattern
- Inconsistency creates need for type adaptation

### Code Section: SVGRenderer Error Handling

**File:** `diagramaid/renderers/svg_renderer.py`
**Lines:** 812-830
**Purpose:** Handle network and encoding errors

```python
except requests.exceptions.Timeout as e:
    raise NetworkError(f"Request timeout after {self.timeout}s") from e
except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response else "unknown"
    raise NetworkError(
        f"Network request failed with status {status_code}"
    ) from e
except requests.exceptions.RequestException as e:
    raise NetworkError(f"Network request failed: {str(e)}") from e
except (UnicodeEncodeError, UnicodeDecodeError) as e:
    context = {
        "mermaid_code_preview": (
            mermaid_code[:100] + "..."
            if len(mermaid_code) > 100
            else mermaid_code
        ),
        "encoding_issue": "unicode",
    }
    raise self.create_detailed_error(e, context) from e
```

**Key Details:**
- Multiple exception types with specific handling
- Context creation for detailed errors
- Custom error types (NetworkError)

### Code Section: PNGRenderer Error Handling

**File:** `diagramaid/renderers/png_renderer.py`
**Lines:** 109-116
**Purpose:** Handle network errors

```python
except requests.exceptions.Timeout as e:
    raise NetworkError(
        f"Request timeout after {self.timeout}s", url=url, timeout=self.timeout
    ) from e
except requests.exceptions.RequestException as e:
    raise NetworkError(f"Network request failed: {str(e)}", url=url) from e
except Exception as e:
    raise RenderingError(f"PNG rendering failed: {str(e)}") from e
```

**Key Details:**
- Similar pattern to SVGRenderer
- Less detailed error context
- url parameter in NetworkError (inconsistent with SVGRenderer)

## Findings

### 1. Duplicated Initialization Patterns

All three renderers (SVGRenderer, PNGRenderer, PDFRenderer) duplicate common initialization logic including:
- Server URL normalization (`server_url.rstrip("/")`)
- Timeout configuration
- No shared base class providing common functionality

**Impact:** Code duplication makes maintenance harder and increases bug surface area.

**Recommendation:** Extract common initialization into BaseRenderer or a shared utility class.

### 2. Inconsistent Caching Implementation

SVGRenderer implements full caching system with:
- Cache key generation
- Cache directory management
- TTL support
- Performance metrics

PNGRenderer has no caching despite making similar network requests. PDFRenderer relies on SVGRenderer's cache indirectly.

**Impact:** Inconsistent performance characteristics across formats. PNG rendering misses optimization opportunity.

**Recommendation:** Either use the centralized CacheManager (which exists in `cache/cache_manager.py`) for all renderers, or clearly document why certain renderers don't use caching.

### 3. Redundant Cache Key Generation

SVGRenderer manually implements cache key generation (`_generate_cache_key` method) using JSON serialization and SHA256 hashing. This duplicates functionality available in `CacheKey` class from `cache/cache_manager.py`.

**Impact:**
- Logic duplication
- Potential inconsistencies in cache key format
- Harder to maintain

**Recommendation:** Replace SVGRenderer's `_generate_cache_key` with `CacheKey.from_content()` from the cache module.

### 4. HTTP Session Management Duplication

SVGRenderer creates and manages requests.Session with:
- Custom headers
- Session reuse via `_create_session()`
- Context manager support (`__enter__`/`__exit__`)

PNGRenderer uses raw `requests.get()` without session reuse, missing:
- Connection pooling benefits
- Custom header configuration
- Consistent User-Agent

**Impact:** PNGRenderer is less efficient due to creating new connections for each request.

**Recommendation:** Extract HTTP session management into a shared utility or base class. All renderers making network requests should reuse sessions.

### 5. Inconsistent Theme Support Interface

Three different approaches to theme support:
- SVGRenderer: Returns `Dict[str, Dict[str, Any]]` with full theme details
- PNGRenderer: Returns `list[str]` with just theme names
- PDFRenderer: Adapts SVGRenderer's return type with type checking

**Impact:**
- Type inconsistency forces runtime type checking
- Theme information duplicated between renderers
- No single source of truth for themes

**Recommendation:** Centralize theme definitions in a ThemeManager class (or use existing `MermaidTheme` from `core.py`) and make all renderers use it consistently.

### 6. Duplicated Error Handling Patterns

Both SVGRenderer and PNGRenderer implement similar error handling for:
- `requests.exceptions.Timeout`
- `requests.exceptions.HTTPError`
- `requests.exceptions.RequestException`

Error handling patterns are similar but with subtle differences (e.g., PNGRenderer passes `url` parameter to NetworkError, SVGRenderer doesn't).

**Impact:** Inconsistent error messages and metadata across renderers.

**Recommendation:** Create a shared error handling utility function or mixin that provides consistent error handling for HTTP operations.

### 7. Underutilized CacheManager

A sophisticated `CacheManager` exists in `cache/cache_manager.py` with:
- Multiple backend support (Memory, File, Redis)
- Eviction strategies
- Performance metrics
- Tag-based clearing
- TTL support

SVGRenderer implements its own caching with file operations instead of using this manager.

**Impact:**
- Code duplication (file operations, TTL checking, etc.)
- Missing features (no Redis support, no eviction strategies in SVGRenderer)
- Maintenance burden

**Recommendation:** Refactor SVGRenderer to use CacheManager. This would eliminate ~100 lines of cache-related code and gain additional features.

### 8. Missing BaseRenderer Utilization

A `BaseRenderer` abstract class exists in `renderers/base.py` with:
- `RendererInfo` structure
- `RenderResult` structure
- `RendererCapability` enum
- Common interface methods

SVGRenderer, PNGRenderer, and PDFRenderer don't inherit from BaseRenderer, duplicating patterns like:
- render() method signatures
- render_to_file() implementations
- Context manager support

**Impact:**
- No type polymorphism
- Inconsistent interfaces
- Duplicated boilerplate code

**Recommendation:** Refactor existing renderers to inherit from BaseRenderer. This provides:
- Consistent interfaces
- Type safety
- Shared functionality
- Better plugin system integration
