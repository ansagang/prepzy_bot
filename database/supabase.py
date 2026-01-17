from supabase import create_client, Client
import os


supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

async def get_subjects():
    subjects = await supabase.table('subjects').select("*").execute()
    return subjects

async def add_subject(state):
    data_state = await state.get_data()
    title = data_state.get('title') 
    slug = data_state.get('slug')
    description = data_state.get('description')
    data = {
        "title": title,
        "slug": slug,
        "description": description
    }
    response = (
        supabase.table('subjects').insert(data).execute()
    )
    return response