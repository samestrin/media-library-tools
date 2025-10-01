#!/usr/bin/env python3
"""
Credential Manager Module for Media Library Tools
Version: 1.0

Provides secure credential resolution from multiple sources with priority order.

Features:
- Multi-source credential resolution (CLI > Environment > Local .env > Global .env)
- Support for local and global .env files
- Quote stripping for common quote characters
- XDG directory standards compliance for global config
- Debug logging for credential source tracking
- Secure handling of API keys and tokens

This module provides shared credential management functionality for tools that need
API keys and other credentials across media library tools.
"""

import os
from pathlib import Path
from typing import Optional


class CredentialManager:
    """Manager for resolving credentials from multiple sources with priority order."""

    def __init__(self, debug: bool = False):
        """
        Initialize credential manager.

        Args:
            debug: Enable debug output for credential source tracking
        """
        self.debug = debug
        self.global_env_path = Path.home() / '.media-library-tools' / '.env'
        self.local_env_path = Path('.env')

    def _log_debug(self, message: str) -> None:
        """Log debug message if debug mode is enabled."""
        if self.debug:
            print(f"DEBUG: {message}")

    def get_credential(self, credential_name: str, cli_value: Optional[str] = None) -> Optional[str]:
        """
        Get credential from multiple sources with priority order.

        Searches for credentials in the following priority order:
        1. CLI argument (highest priority)
        2. Environment variable
        3. Local .env file (current directory)
        4. Global .env file (~/.media-library-tools/.env)

        Args:
            credential_name: Name of the credential (e.g., 'TVDB_API_KEY')
            cli_value: Value from CLI argument (takes highest priority)

        Returns:
            The credential value with quotes stripped, or None if not found

        Example:
            >>> manager = CredentialManager()
            >>> api_key = manager.get_credential('TVDB_API_KEY', cli_value=args.api_key)
            >>> if not api_key:
            ...     print("Error: TVDB_API_KEY not found")
        """
        # First check CLI argument
        if cli_value:
            self._log_debug(f"Found {credential_name} from CLI argument")
            return cli_value.strip('"\'')

        # Then check environment variable
        env_value = os.environ.get(credential_name)
        if env_value:
            self._log_debug(f"Found {credential_name} in environment variable")
            return env_value.strip('"\'')

        # Check local .env file
        if self.local_env_path.exists():
            try:
                with open(self.local_env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f'{credential_name}='):
                            value = line.split('=', 1)[1].strip()
                            self._log_debug(f"Found {credential_name} in local .env file")
                            return value.strip('"\'')
            except (IOError, OSError) as e:
                self._log_debug(f"Could not read local .env file: {e}")

        # Finally check global .env file
        if self.global_env_path.exists():
            try:
                with open(self.global_env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f'{credential_name}='):
                            value = line.split('=', 1)[1].strip()
                            self._log_debug(f"Found {credential_name} in global .env file")
                            return value.strip('"\'')
            except (IOError, OSError) as e:
                self._log_debug(f"Could not read global .env file: {e}")

        return None

    def require_credential(self, credential_name: str, cli_value: Optional[str] = None,
                          error_message: Optional[str] = None) -> str:
        """
        Get credential or raise error if not found.

        Convenience method that calls get_credential() and raises a descriptive
        error if the credential is not found.

        Args:
            credential_name: Name of the credential to retrieve
            cli_value: Value from CLI argument (takes highest priority)
            error_message: Custom error message (default: auto-generated)

        Returns:
            The credential value

        Raises:
            ValueError: If credential is not found in any source

        Example:
            >>> manager = CredentialManager()
            >>> try:
            ...     api_key = manager.require_credential('TVDB_API_KEY')
            ... except ValueError as e:
            ...     print(f"Error: {e}")
            ...     sys.exit(1)
        """
        credential = self.get_credential(credential_name, cli_value)
        if credential is None:
            if error_message:
                raise ValueError(error_message)
            else:
                raise ValueError(
                    f"{credential_name} not found. Please provide via:\n"
                    f"  1. CLI argument\n"
                    f"  2. Environment variable: export {credential_name}='value'\n"
                    f"  3. Local .env file: echo '{credential_name}=value' >> .env\n"
                    f"  4. Global .env file: echo '{credential_name}=value' >> ~/.media-library-tools/.env"
                )
        return credential

    def get_multiple_credentials(self, *credential_specs) -> dict:
        """
        Get multiple credentials at once.

        Args:
            *credential_specs: Variable number of tuples (credential_name, cli_value, required)

        Returns:
            Dictionary mapping credential names to values

        Raises:
            ValueError: If any required credential is not found

        Example:
            >>> manager = CredentialManager()
            >>> creds = manager.get_multiple_credentials(
            ...     ('TVDB_API_KEY', args.tvdb_key, True),
            ...     ('PLEX_TOKEN', args.plex_token, False)
            ... )
            >>> tvdb_key = creds['TVDB_API_KEY']
            >>> plex_token = creds.get('PLEX_TOKEN')  # May be None
        """
        credentials = {}

        for spec in credential_specs:
            if len(spec) == 2:
                credential_name, cli_value = spec
                required = False
            elif len(spec) == 3:
                credential_name, cli_value, required = spec
            else:
                raise ValueError(f"Invalid credential spec: {spec}")

            if required:
                credentials[credential_name] = self.require_credential(credential_name, cli_value)
            else:
                credential = self.get_credential(credential_name, cli_value)
                if credential is not None:
                    credentials[credential_name] = credential

        return credentials

    def create_global_env_template(self, credentials: list) -> bool:
        """
        Create global .env template file with specified credential names.

        Creates the global .env directory and a template file with placeholder
        values for the specified credentials.

        Args:
            credentials: List of credential names to include in template

        Returns:
            True if template created successfully, False otherwise

        Example:
            >>> manager = CredentialManager()
            >>> manager.create_global_env_template(['TVDB_API_KEY', 'PLEX_TOKEN'])
        """
        try:
            # Create directory if it doesn't exist
            self.global_env_path.parent.mkdir(parents=True, exist_ok=True)

            # Don't overwrite existing file
            if self.global_env_path.exists():
                self._log_debug(f"Global .env file already exists at {self.global_env_path}")
                return False

            # Create template
            with open(self.global_env_path, 'w') as f:
                f.write("# Media Library Tools - Global Configuration\n")
                f.write("# Add your credentials below\n\n")
                for cred in credentials:
                    f.write(f"{cred}=your_{cred.lower()}_here\n")

            self._log_debug(f"Created global .env template at {self.global_env_path}")
            return True

        except (IOError, OSError) as e:
            self._log_debug(f"Failed to create global .env template: {e}")
            return False
