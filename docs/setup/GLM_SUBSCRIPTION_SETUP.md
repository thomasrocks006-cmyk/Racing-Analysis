# GLM Pro Subscription - Account Setup

## ✅ Current Status
- API Key: **Valid** ✓
- Model Access: **glm-4-plus available** ✓
- Issue: **Need to activate subscription quota/credits**

## 🎯 How to Use Your Pro Subscription

Your GLM Pro subscription needs to be properly activated. Here's how:

### Option 1: Activate Subscription Package (Recommended)

1. **Go to your account**: https://open.bigmodel.cn/usercenter/overview

2. **Check your subscription status**:
   - Look for "会员套餐" (Membership Package)
   - Verify your Pro subscription is active
   - Check if resource package is attached

3. **Activate resource package**:
   - Go to: https://open.bigmodel.cn/usercenter/resourcepack
   - If you have a Pro subscription, you should have monthly quota
   - Make sure the resource package is **activated** and **bound to your account**

4. **Verify API Key is linked to subscription**:
   - Go to: https://open.bigmodel.cn/usercenter/apikeys
   - Make sure your API key shows the subscription plan
   - If not, create a new API key under your Pro account

### Option 2: Add Account Balance

If your Pro subscription doesn't include API access quota:

1. **Go to**: https://open.bigmodel.cn/usercenter/recharge

2. **Add balance** (充值):
   - Minimum usually ¥10-50 RMB
   - This gives you pay-per-use credits

3. **Use your existing API key**:
   - Your current key will work once balance is added
   - No need to regenerate

### Option 3: Check Subscription Includes API Access

Some Pro subscriptions are for the web interface only:

1. **Verify your plan includes**:
   - "API调用" (API calls)
   - "开发者接口" (Developer interface)

2. **If not included**:
   - You may need to upgrade to "Pro + API" plan
   - Or purchase an API resource package separately

3. **Contact support** if unclear:
   - https://open.bigmodel.cn/
   - Check their pricing page for API access details

## 🔍 Verify Your Setup

Once you've activated your quota or added balance:

```bash
make verify-glm
```

You should see:
```
✅ API connection successful!
   Model responded: Hello
```

## 💡 Understanding GLM Pricing Models

### Pro Subscription (Web)
- Access to GLM-4 via web interface
- May NOT include API access
- Usually ¥99-199/month

### Pro + API Access
- Web interface access
- API calls with monthly quota
- Usually includes X million tokens/month

### Pay-Per-Use (No Subscription)
- Just add account balance
- Pay per API call
- No monthly fee

## ⚙️ Your Configuration is Ready!

Once your account is set up, everything will work automatically:

1. **Continue Extension** → Uses your API key
2. **GLM-4-Plus model** → Available with your subscription
3. **Press Ctrl+L** → Start chatting!

## 🆘 Troubleshooting

### "余额不足" (Insufficient Balance)
→ Add balance or activate subscription resource package

### "无可用资源包" (No Available Resource Package)
→ Your Pro subscription may not include API quota
→ Purchase API resource package or add pay-per-use balance

### Still not working?
→ Contact Zhipu AI support
→ Verify your specific subscription plan includes API access
→ They can clarify what your Pro plan includes

## 📞 Zhipu AI Support

- Website: https://open.bigmodel.cn/
- Check pricing: https://open.bigmodel.cn/pricing
- Documentation: https://open.bigmodel.cn/dev/api

---

## Summary

**Your setup is complete!** You just need to:

1. ✅ Activate your Pro subscription's API quota/resource package
   OR
2. ✅ Add account balance for pay-per-use

Then run: `make verify-glm` and you're ready to code! 🚀
