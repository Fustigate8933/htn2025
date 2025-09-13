def generate_avatar(face_image_path: str, voice_sample_path: str, avatar_type: str) -> str:
    # call avatar api
    return f"Generated {avatar_type} avatar based on {face_image_path} and {voice_sample_path}"