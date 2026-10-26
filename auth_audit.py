"""
Phase 1F: Authentication Architecture Audit
Inspect current authentication implementation
"""

import os
import re

print("=" * 70)
print("PHASE 1F: AUTHENTICATION ARCHITECTURE AUDIT")
print("=" * 70)

# Search for authentication implementations
web_app_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\apps\web"
api_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\apps\api"

print("\n" + "=" * 70)
print("FRONTEND AUTHENTICATION")
print("=" * 70)

# Check for AuthContext
auth_context_path = os.path.join(web_app_path, "app", "components", "AuthContext.tsx")
if os.path.exists(auth_context_path):
    print(f"[PASS] AuthContext.tsx exists")
    with open(auth_context_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'DevAuthService' in content:
            print("[INFO] Uses DevAuthService (mock authentication)")
        if 'supabase.auth' in content:
            print("[INFO] Uses Supabase Auth")
        if 'getCurrentUser' in content:
            print("[INFO] Has getCurrentUser function")
else:
    print("[FAIL] AuthContext.tsx NOT found")

# Check for AuthModal
auth_modal_path = os.path.join(web_app_path, "app", "components", "AuthModal.tsx")
if os.path.exists(auth_modal_path):
    print(f"[PASS] AuthModal.tsx exists")
    with open(auth_modal_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'supabase.auth' in content:
            print("[INFO] Uses Supabase Auth for login/signup")
else:
    print("[FAIL] AuthModal.tsx NOT found")

print("\n" + "=" * 70)
print("BACKEND AUTHENTICATION")
print("=" * 70)

# Check API app.ts
api_app_path = os.path.join(api_path, "src", "app.ts")
if os.path.exists(api_app_path):
    print(f"[PASS] API app.ts exists")
    with open(api_app_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'DevAuthService' in content:
            print("[INFO] Uses DevAuthService")
        if 'auth' in content.lower():
            print("[INFO] Has auth-related code")
        if 'DATABASE_URL' in content:
            print("[INFO] Checks for DATABASE_URL")
else:
    print("[FAIL] API app.ts NOT found")

# Check for auth-core package
auth_core_path = r"C:\Users\Nusaiba\Desktop\Ai Breand\packages\auth-core"
if os.path.exists(auth_core_path):
    print(f"[PASS] auth-core package exists")
    # Check package.json
    pkg_json = os.path.join(auth_core_path, "package.json")
    if os.path.exists(pkg_json):
        with open(pkg_json, 'r') as f:
            print("[INFO] auth-core is a package")
else:
    print("[INFO] No auth-core package")

print("\n" + "=" * 70)
print("AUTHENTICATION SUMMARY")
print("=" * 70)

print("\nCurrent Implementation:")
print("  Frontend: Likely uses Supabase Auth (AuthContext, AuthModal)")
print("  Backend: Uses DevAuthService (mock)")
print("  Connection: Frontend auth independent of backend mock")

print("\nImplications:")
print("  - Frontend can have real Supabase user sessions")
print("  - Backend identity is currently mocked")
print("  - For chat persistence: Need to use auth.uid() from Supabase")
print("  - Backend API may need to verify Supabase JWT tokens")

print("\n" + "=" * 70)
print("AUTHENTICATION AUDIT COMPLETE")
print("=" * 70)
