from supabase import create_client, Client
import os
import random


supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

async def get_mocks(subject=None):
    if subject is not None:
        response = (
            supabase.table('mocks').select("*").eq("subject", subject).execute()
        )
        return response
    else:
        response = (
            supabase.table('mocks').select("*").execute()
        )
        return response

async def get_mock(id):
    mocks = (
        supabase.table('mocks').select("*").eq("id", id).execute()
    )
    return mocks

async def get_random_mock():
    mocks = (
        supabase.table('mocks').select("*").execute()
    )
    if len(mocks.data) > 0:
        mock = random.choice(mocks.data)
        return mock
    else:
        return None

async def get_random_material():
    materials = (
        supabase.table('materials').select("*").execute()
    )
    if len(materials.data) > 0:
        material = random.choice(materials.data)
        return material
    else:
        return None

async def get_subjects():
    subjects = (
        supabase.table('subjects').select("*").execute()
    )
    return subjects

async def get_subject(slug):
    subjects = (
        supabase.table('subjects').select("*").eq("slug", slug).execute()
    )
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

async def add_material(state):
    data_state = await state.get_data()
    title = data_state.get('title') 
    file = data_state.get('file')
    subject = data_state.get('subject')
    data = {
        "title": title,
        "filename": file,
        "subject": subject
    }
    response = (
        supabase.table('materials').insert(data).execute()
    )
    return response

async def add_mock(state):
    data_state = await state.get_data()
    title = data_state.get('title') 
    file = data_state.get('file')
    subject = data_state.get('subject')
    data = {
        "title": title,
        "filename": file,
        "subject": subject
    }
    response = (
        supabase.table('mocks').insert(data).execute()
    )
    return response

async def delete_subject(slug):
    response = (
        supabase.table('subjects').delete().eq("slug", slug).execute()
    )
    return response

async def delete_material(id):
    response = (
        supabase.table('materials').delete().eq("id", id).execute()
    )
    return response

async def delete_mock(id):
    response = (
        supabase.table('mocks').delete().eq("id", id).execute()
    )
    return response

async def get_materials(subject=None):
    if subject is not None:
        response = (
            supabase.table('materials').select("*").eq("subject", subject).execute()
        )
        return response
    else:
        response = (
            supabase.table('materials').select("*").execute()
        )
        return response

async def get_material(id):
    response = (
        supabase.table('materials').select("*").eq("id", id).execute()
    )
    return response

async def get_material_file(filename):
    # response = supabase.storage.from('portfolio').getPublicUrl('projects/'+media)
    response = supabase.storage.from_('media').get_public_url("materials/"+filename)
    return response

# async def add_material_file(file, filename):
#     with open("./materials/", "rb") as file:
#         response = (
#             supabase.storage
#             .from_("media")
#             .upload(
#                 file=file,
#                 path="materials/",
#                 file_options={"cache-control": "3600", "upsert": "false"}
#             )
#     )
#     return response