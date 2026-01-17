from keyboards import inline_builder

def inlineKb(isAdmin):
    if isAdmin:
        return admin_kb
    else:
        return client_kb
    
text_client = ["❓", "📚 Materials", "📄 Mocks", "⚡️ Practice", "🏆 Leaderboard"]
callback_client = ["help", "materials", "mocks", "practices", "leadboard"]
sizes_client = [1, 2, 2]

text_admin = ["❓", "📚 Materials", "📄 Mocks", "⚡️ Practice", "🏆 Leaderboard", "✅ Add", "❌ Delete"]
calback_admin = ["help", "materials", "mocks", "testing", "leaderboard", "add", "delete_", "post"]
sizes_admin = [1, 2, 2, 2]

client_kb = inline_builder(text=text_client, callback_data=callback_client, sizes=sizes_client)

admin_kb = inline_builder(text=text_admin, callback_data=calback_admin, sizes=sizes_admin)