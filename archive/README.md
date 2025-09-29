# Archive Directory

This directory contains development artifacts and debugging scripts that were used during the development and debugging phases of the GHX Price Validation Tool.

## Contents

### development_scripts/
Contains all debugging and testing scripts used during development:

- `debug_*.py` - Various debugging utilities for specific components
- `test_*.py` - Development test scripts
- `investigate_*.py` - Investigation scripts for specific issues
- `performance_benchmark.py` - Performance testing utilities
- `generate_validation_test_file.py` - Test data generation

These files were essential during development but are not needed for the production clean architecture.

## Purpose

These files are archived to:
1. Preserve development history and debugging methods
2. Keep the main project directory clean and focused
3. Allow future reference if debugging similar issues
4. Maintain a record of the problem-solving process

## Usage

These scripts can be moved back to the main directory if needed for debugging or development purposes.

## Clean Architecture

The production system now uses the clean `validator/` package architecture with proper separation of concerns and comprehensive documentation.