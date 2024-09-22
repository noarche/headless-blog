import os
import re
import datetime
from pathlib import Path
from jinja2 import Template

# Configuration
POST_DIR = './post/'
TEMPLATE_DIR = './template/'
WWW_DIR = './www_html/'
FAVICON = 'favicon.ico'
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, 'template.html')

# Helper functions
def get_word_count(text):
    return len(text.split())

def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 ** 2)  # Size in MB

def format_size(size_in_mb):
    if size_in_mb < 1:
        return f"{size_in_mb * 1024:.2f} KB"
    elif size_in_mb < 1024:
        return f"{size_in_mb:.2f} MB"
    elif size_in_mb < 1024 ** 2:
        return f"{size_in_mb / 1024:.2f} GB"
    else:
        return f"{size_in_mb / (1024 ** 2):.2f} TB"

def format_text(text):
    # Convert [h1], [h2], [h3] to headers
    formatted_text = re.sub(r'^\[h1\](.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    formatted_text = re.sub(r'^\[h2\](.*?)$', r'<h2>\1</h2>', formatted_text, flags=re.MULTILINE)
    formatted_text = re.sub(r'^\[h3\](.*?)$', r'<h3>\1</h3>', formatted_text, flags=re.MULTILINE)

    # Replace consecutive blank lines with <br /><br />
    formatted_text = re.sub(r'(\n\s*\n)', '<br /><br />', formatted_text)

    # Convert single new lines within paragraphs to just line breaks (if needed)
    formatted_text = re.sub(r'(?<!\n)\n(?!\n)', '<br />', formatted_text)
    
    # Convert [Link Text](url) to HTML link
    formatted_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', formatted_text)

    # Convert [b]text to HTML bold at line start
    formatted_text = re.sub(r'^\[b\](.*?)$', r'<b>\1</b>', formatted_text, flags=re.MULTILINE)
    formatted_text = re.sub(r'\[b\](.*?)\[/b\]', r'<b>\1</b>', formatted_text)

    return formatted_text


def get_post_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        formatted_text = format_text(text)
        word_count = get_word_count(formatted_text)
        return {
            'title': Path(file_path).stem.replace(' ', '_'),
            'date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%A %b %d %Y %H:%M'),
            'word_count': word_count,
            'content': formatted_text
        }

def generate_html(posts, page, total_pages, total_word_count, site_size, last_update):
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = Template(f.read())

    return template.render(
        posts=posts,
        page=page,
        total_pages=total_pages,
        total_word_count=total_word_count,
        site_size=site_size,
        last_update=last_update,
        favicon=FAVICON
    )

def generate_index_page(posts, page_number, total_pages, total_word_count, site_size, last_update):
    if page_number == 1:
        file_name = 'index.html'
    else:
        file_name = f'page_{page_number}.html'

    html_content = generate_html(posts, page_number, total_pages, total_word_count, site_size, last_update)
    with open(os.path.join(WWW_DIR, file_name), 'w', encoding='utf-8') as f:
        f.write(html_content)

def create_post_pages(posts):
    for post in posts:
        file_name = f"{post['title']}.html"
        post_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="icon" type="image/x-icon" href="{FAVICON}">
            <title>{post['title'].replace('_', ' ')}</title>
            <style>
                body {{
                    font-family: 'Trebuchet MS', Arial, sans-serif;
                    background-color: #000000;
                    color: #FFFFFF;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #1E1E1E;
                }}
                a {{
                    color: #FF0000;
                    text-decoration: none;
                }}
                .footer {{
                    margin-top: 20px;
                    padding: 10px 0;
                    border-top: 1px solid #333;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{post['title'].replace('_', ' ')}</h1>
                <div>{post['content']}</div>
                <div class="footer">
                    <p><a href="index.html">Home</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        with open(os.path.join(WWW_DIR, file_name), 'w', encoding='utf-8') as f:
            f.write(post_html)

def main():
    os.makedirs(WWW_DIR, exist_ok=True)
    
    posts = []
    for file in Path(POST_DIR).glob('*.txt'):
        metadata = get_post_metadata(file)
        posts.append(metadata)

    posts.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%A %b %d %Y %H:%M'), reverse=True)

    total_word_count = sum(post['word_count'] for post in posts)
    site_size = sum(get_file_size(file) for file in Path(POST_DIR).glob('*.txt'))
    last_update = datetime.datetime.now().strftime('%A %b %d %Y %H:%M')

    total_pages = (len(posts) - 1) // 10 + 1

    for page in range(1, total_pages + 1):
        start = (page - 1) * 10
        end = start + 10
        page_posts = posts[start:end]
        generate_index_page(page_posts, page, total_pages, total_word_count, format_size(site_size), last_update)

    create_post_pages(posts)

if __name__ == '__main__':
    main()
