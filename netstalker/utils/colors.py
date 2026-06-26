"""Color codes for terminal output."""


class ColorScheme:
    """ANSI color codes."""
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    
    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Background
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    
    @staticmethod
    def success(text: str) -> str:
        """Format success message."""
        return f"{ColorScheme.GREEN}[+]{ColorScheme.RESET} {text}"
    
    @staticmethod
    def error(text: str) -> str:
        """Format error message."""
        return f"{ColorScheme.RED}[!]{ColorScheme.RESET} {text}"
    
    @staticmethod
    def warning(text: str) -> str:
        """Format warning message."""
        return f"{ColorScheme.YELLOW}[*]{ColorScheme.RESET} {text}"
    
    @staticmethod
    def info(text: str) -> str:
        """Format info message."""
        return f"{ColorScheme.BLUE}[i]{ColorScheme.RESET} {text}"
