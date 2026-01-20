from supabase import create_client, Client
import os
import random


supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def get_distinct_values(arr):
    new_arr = []
    for x in arr:
        if x not in new_arr:
            new_arr.append(x)

    return new_arr

def distinct_by(rows, key):
    seen = set()
    result = []

    for row in rows:
        value = row[key]
        if value not in seen:
            seen.add(value)
            result.append(row)

    return result

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

async def add_practice(state):
    data_state = await state.get_data()
    slug =  data_state.get('slug')
    answer = data_state.get('answer') 
    file = data_state.get('file')
    subject = data_state.get('subject')
    number = data_state.get('number')
    title = data_state.get('title')
    question = data_state.get('question')
    data = {
        "answer": answer,
        "filename": file,
        "subject": subject,
        "number": number,
        "slug": slug,
        "title": title,
        "question": question
    }
    response = (
        supabase.table('practices').insert(data).execute()
    )
    return response

async def get_practice_slug():
    response = (
        supabase.table("practices").select("slug").execute()
    )

    slugs = get_distinct_values(response.data)
    print(slugs)
    return slugs

async def get_practices(subject):
    practices = (
        supabase.table("practices").select("*").eq("subject", subject).execute()
    )

    return distinct_by(practices.data, "slug")

async def get_practice(slug):
    practice = (
        supabase.table("practices").select("*").eq("slug", slug).order("subject").order("number", desc=False).execute()
    )

    if len(practice.data) > 0:
        return practice.data[-1]
    else:
        return []
    
async def get_practices_full(slug):
    practice = (
        supabase.table("practices").select("*").eq("slug", slug).order("subject").order("number", desc=False).execute()
    )

    return practice.data

async def delete_practice(slug):
    response = (
        supabase.table('practices').delete().eq("slug", slug).execute()
    )
    return response

async def add_score(id_: int, practice):
    data = {
        "id_": id_,
        "practice": practice,
        "username": "",
        "current_question": 0,
        "questions_passed": 0,
        "questions_message": 0,
        "in_process": 0,
        "result": "0"
    }
    response = (
        supabase.table('scores').insert(data).execute()
    )
    return response

async def delete_score(id_: int, practice):
    response = (
        supabase.table('scores').delete().eq("id_", id_).eq("practice", practice).execute()
    )

    return response

async def exists(id_: int, practice):
    response = (
        supabase.table('scores').select("*").eq("id_", id_).eq("practice", practice).execute()
    )

    return bool(response.data)

async def set_in_process(id_: int, x: bool, practice):
    data = {
        "in_process": x
    }
    response = (
        supabase.table('scores').update(data).eq("id_", id_).eq("practice", practice).execute()
    )
    return response

async def is_in_process(id_: int, practice):
    practice = (
        supabase.table("scores").select("").eq("id_", id_).eq("practice", practice).single().execute()
    )
    return practice.data['in_process']

async def get_current_questions(id_: int, practice):
    practice = (
        supabase.table("scores").select("current_question").eq("id_", id_).eq("practice", practice).single().execute()
    )

    return practice.data

async def update_current_question(id_: int, x: int, practice):
    data = {
        "current_question": x
    }
    response = (
        supabase.table('scores').update(data).eq("id_", id_).eq("practice", practice).execute()
    )
    return response

async def update_questions_passed(id_: int, x: int, practice):
    data = {
        "questions_passed": x
    }
    response = (
        supabase.table('scores').update(data).eq("id_", id_).eq("practice", practice).execute()
    )
    return response

async def get_questions_passed(id_: int, practice):
    practice = (
        supabase.table("scores").select("questions_passed").eq("id_", id_).eq("practice", practice).single().execute()
    )

    return practice.data

async def get_questions_message(id_: int, practice):
    practice = (
        supabase.table("scores").select("questions_message").eq("id_", id_).eq("practice", practice).single().execute()
    )

    return practice.data

async def update_questions_message(id_: int, x: int, practice):
    data = {
        "questions_message": x
    }
    response = (
        supabase.table('scores').update(data).eq("id_", id_).eq("practice", practice).execute()
    )
    return response

async def change_score(id_:int, practice, result, username):
    data = {
        "result": result,
        "username": username
    }
    response = (
        supabase.table('scores').update(data).eq("id_", id_).eq("practice", practice).execute()
    )
    return response

async def get_leaderboard(username):
    response = (
        supabase.table("scores").select("*").eq("username", username).order("result", desc=True).execute()
    )

    return response.data