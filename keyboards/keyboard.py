from keyboards import inline_builder

def inlineKb(isAdmin):
    if isAdmin:
        return admin_kb
    else:
        return client_kb

text_client = ["❓", "Scores", "📚 Subjects", "📖 Materials", "📄 Mocks", "⚡️ Practice"]
callback_client = ["help", "scores", "subjects", "materials", "mocks", "practice"]
sizes_client = [1, 1, 2, 2]

text_admin = ["❓", "Scores", "📚 Subjects", "📖 Materials", "📄 Mocks", "⚡️ Practice", "✅ Add", "❌ Delete"]
callback_admin = ["help", "scores", "subjects", "materials", "mocks", "practices", "add", "delete_"]
sizes_admin = [1, 1, 2, 2, 2]

client_kb = inline_builder(text=text_client, callback_data=callback_client, sizes=sizes_client)

admin_kb = inline_builder(text=text_admin, callback_data=callback_admin, sizes=sizes_admin)