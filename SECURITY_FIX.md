# Security Fix: Cache Page Decorator Issue

## Issue Identified

**Django Bug #15855**: Using `@cache_page` with `@vary_on_headers('Cookie')` is a security vulnerability.

 

