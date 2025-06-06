#!/bin/bash

echo "🚀 Claude Cost - Ready to Publish!"
echo "=================================="

echo ""
echo "📋 Quick Setup Commands:"
echo ""

echo "1️⃣ Initialize Git Repository:"
echo "git init"
echo "git add ."
echo "git commit -m \"Initial release: Privacy-first Claude usage analysis tool\""
echo "git branch -M main"

echo ""
echo "2️⃣ Create GitHub Repository:"
echo "🌐 Go to: https://github.com/new"
echo "📝 Repository name: claude-cost"
echo "📄 Description: Privacy-first Claude usage analysis and cost optimization tool"
echo "✅ Public repository"
echo "❌ Don't initialize with README (we have one)"

echo ""
echo "3️⃣ Connect and Push:"
echo "git remote add origin https://github.com/hassanazam/claude-cost.git"
echo "git push -u origin main"

echo ""
echo "4️⃣ Set Up PyPI (one-time):"
echo "🌐 Create PyPI account: https://pypi.org/account/register/"
echo "🔑 Generate API token: https://pypi.org/manage/account/token/"
echo "⚙️  Add to GitHub Secrets: Settings > Secrets > Actions > New secret"
echo "   Name: PYPI_API_TOKEN"
echo "   Value: [your-token]"

echo ""
echo "5️⃣ Publish to PyPI:"
echo "git tag v1.0.0"
echo "git push origin v1.0.0"
echo "🌐 Create release: https://github.com/hassanazam/claude-cost/releases/new"

echo ""
echo "🎉 After publishing, users can install with:"
echo "pip install claude-cost"

echo ""
echo "✅ Everything is ready! Just run the commands above."