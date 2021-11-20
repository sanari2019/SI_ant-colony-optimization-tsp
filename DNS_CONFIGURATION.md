# DNS Configuration for tsp.samuelanari-rsg.com

## Quick Setup Guide

### Namecheap DNS Settings

**Login**: [namecheap.com](https://www.namecheap.com)

**Domain**: samuelanari-rsg.com

**Location**: Domain List → Manage → Advanced DNS

---

## DNS Record Configuration

### Option 1: CNAME Record (Recommended)

| Field | Value |
|-------|-------|
| **Type** | CNAME Record |
| **Host** | `tsp` |
| **Value** | `cname.vercel-dns.com` |
| **TTL** | Automatic |

**Result**: `tsp.samuelanari-rsg.com` → Vercel

---

### Option 2: A Record (Alternative)

| Field | Value |
|-------|-------|
| **Type** | A Record |
| **Host** | `tsp` |
| **Value** | `76.76.21.21` |
| **TTL** | Automatic |

**Note**: Get the exact IP from Vercel dashboard after adding domain

---

## Step-by-Step Instructions

### 1. Access Namecheap DNS

1. Login to Namecheap
2. Click "Domain List" in left sidebar
3. Find `samuelanari-rsg.com`
4. Click "Manage" button

### 2. Navigate to DNS Settings

1. Click "Advanced DNS" tab
2. Scroll to "Host Records" section

### 3. Add New Record

1. Click "Add New Record" button
2. Fill in the values from Option 1 (CNAME) above
3. Click green checkmark to save
4. Click "Save All Changes" button at top

### 4. Verify Configuration

After 15-30 minutes, check:

```bash
# Command Prompt / Terminal
nslookup tsp.samuelanari-rsg.com
```

Expected output:
```
Non-authoritative answer:
Name:    tsp.samuelanari-rsg.com
Address: 76.76.21.21
```

---

## Vercel Domain Setup

### 1. Add Domain in Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your ACO TSP project
3. Click "Settings" → "Domains"
4. Click "Add" button
5. Enter: `tsp.samuelanari-rsg.com`
6. Click "Add"

### 2. Note DNS Information

Vercel will display required DNS configuration:
- Copy the CNAME target: `cname.vercel-dns.com`
- Use this in Namecheap (see above)

### 3. Wait for Verification

- Status will show "Pending" initially
- Changes to "Valid" after DNS propagates
- Usually takes 15-30 minutes
- SSL certificate auto-provisions when valid

---

## Verification Checklist

After DNS propagation:

- [ ] Vercel domain status shows "Valid"
- [ ] SSL certificate shows "Issued"
- [ ] `https://tsp.samuelanari-rsg.com` loads
- [ ] No SSL warnings in browser
- [ ] Site is accessible worldwide

Test with:
- [dnschecker.org](https://dnschecker.org)
- [whatsmydns.net](https://whatsmydns.net)

---

## Troubleshooting

### DNS Not Resolving

**Check**:
```bash
nslookup tsp.samuelanari-rsg.com
```

**If fails**:
1. Wait 30 more minutes
2. Verify CNAME record is correct
3. Ensure no conflicting A records exist
4. Clear local DNS cache:
   ```bash
   # Windows
   ipconfig /flushdns

   # macOS
   sudo dscacheutil -flushcache

   # Linux
   sudo systemd-resolve --flush-caches
   ```

### SSL Certificate Pending

**Solution**:
1. Ensure DNS is fully propagated
2. Check domain status in Vercel is "Valid"
3. Wait 10 minutes for auto-provisioning
4. If still pending, contact Vercel support

---

## DNS Propagation Time

**Typical Timeline**:
- Minimum: 5 minutes
- Average: 15-30 minutes
- Maximum: 48 hours (rare)

**Check Status**:
- [dnschecker.org](https://dnschecker.org)
- Shows propagation across global DNS servers
- Green checkmarks = propagated

---

## Important Notes

1. **No WWW**: This configuration is for `tsp.samuelanari-rsg.com` (subdomain only)

2. **Main Domain Unaffected**: `samuelanari-rsg.com` remains unchanged

3. **Free SSL**: Vercel provides free SSL certificate (Let's Encrypt)

4. **Auto-Renewal**: SSL certificate renews automatically

5. **No Email Impact**: DNS changes don't affect email (if configured)

---

## Current Configuration Summary

**Your Domain**: `samuelanari-rsg.com` (Namecheap)

**Subdomain**: `tsp.samuelanari-rsg.com`

**Hosting**: Vercel

**Application**: Advanced ACO TSP Visualizer

**SSL**: Automatic (Vercel)

**Cost**: $0 (Vercel free tier)

---

## Contact Information

**Vercel Support**: [vercel.com/support](https://vercel.com/support)

**Namecheap Support**: [namecheap.com/support](https://www.namecheap.com/support)

**DNS Help**: help@namecheap.com

---

Last Updated: 2025-11-18
