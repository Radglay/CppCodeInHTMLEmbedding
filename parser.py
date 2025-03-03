from bs4 import BeautifulSoup
import os
import re
import sys
from pathlib import Path


soup = BeautifulSoup()


SOURCES_STRUCTURE = {}

SRC_DIR = "src"
HTML_DIR = "questions"


def update_sources_structure(file_path):
    global SOURCES_STRUCTURE
    current_dict = SOURCES_STRUCTURE

    dirs = file_path.split(os.sep)
    file_name = dirs.pop()

    for dir_name in dirs:
        if dir_name not in current_dict.keys():
            current_dict[dir_name] = {}

        current_dict = current_dict[dir_name]
    

    if file_name.endswith(".cpp"):
        if "sources" not in current_dict.keys():
            current_dict["sources"] = []        
        current_dict["sources"].append(file_name)

    elif file_name.endswith(".md"):
        if "md" not in current_dict.keys():
            current_dict["md"] = []
        current_dict["md"].append(file_name)

    elif file_name.endswith(".h") or file_name.endswith(".hpp"):
        if "headers" not in current_dict.keys():
            current_dict["headers"] = []
        current_dict["headers"].append(file_name)

    elif file_name.endswith(".txt"):
        if "text" not in current_dict.keys():
            current_dict["text"] = []
        current_dict["text"].append(file_name)


def is_question(dictionary):
    return "sources" in dictionary.keys() or\
           "md" in dictionary.keys() or\
           "headers" in dictionary.keys() or\
           "text" in dictionary.keys()


def create_question(dir_name, question_path):
    question = soup.new_tag("li")
    question['class'] = 'question'
    question['style'] = 'margin-left:1em;'

    link = soup.new_tag('a')
    link.string = dir_name
    link['href'] = question_path

    question.append(link)
    return question


def create_directory(dir_name):
    directory = soup.new_tag("div")
    directory['class'] = 'directory'

    directory_name = soup.new_tag("div")
    directory_name['class'] = 'directory-name'
    directory_name['onclick'] = 'toggleDirectory(event)'
    directory_name.string = dir_name

    directory_content = soup.new_tag("ul")
    directory_content['class'] = 'directory-content'
    directory_content['style'] = 'list-style: none;'
   
    directory.append(directory_name)
    directory.append(directory_content)
    return directory


def parse_readme(readme_file_path, result_container):
    with open(readme_file_path) as readme:
        content = readme.read()
        result_container.append(create_godbolt_link(content))
        result_container.append(create_result_value(content))


def create_godbolt_link(readme_content):
    result = re.search("(\*\*godbolt\*\*:)([ ]*)([\s\S]*)", readme_content)
    godbolt_link = soup.new_tag("a")
    godbolt_link['class'] = 'online-compiler-link'
    godbolt_link['href'] = result.group(3)
    godbolt_link.string = 'online-compiler-link'
    return godbolt_link


def create_result_value(readme_content):
    result_value = soup.new_tag('div')
    result_value['class'] = 'result-value'

    result_title = soup.new_tag('div')
    result_title.string = 'Result:'
    result_title['class'] = 'result-title'
    result_title['onclick'] = 'toggleResult(event)'
    result_title['style'] = 'color:white;'
    result_title['style'] += 'background-color: rgb(42, 41, 41);'
    result_title['style'] += 'width: 100ch;'
   
    result = re.search("(\*\*result\*\*:)([ \n]*)([\s\S]*?)(?=\*\*godbolt\*\*)", readme_content)
    pre = soup.new_tag('pre')
    pre['style'] = 'display: none'
    pre.string = result.group(3)

    result_value.append(result_title)
    result_value.append(pre)

    return result_value


def get_code_file_content(file_path):
    pre = soup.new_tag("pre")
    code = soup.new_tag("code")

    with open(file_path) as file:
        code.string = file.read().strip()
    pre.append(code)

    return pre


def generate_question_html(html_file_path, cpp_sources_dir, dictionary):
    dirname = os.path.dirname(html_file_path)
    basename = os.path.basename(html_file_path)
    final_dir = os.path.splitext(basename)[0]
    source_dir = os.path.join(dirname, final_dir).replace("questions", cpp_sources_dir)

    if not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)

    html = soup.new_tag("html")
    head = soup.new_tag("head")
    script = soup.new_tag("script")
    script.string = '''
    function toggleResult(event)
    {
        const parentNode = event.target.parentNode;
        let preTag = parentNode.getElementsByTagName("pre")[0];

        if (preTag.style.display == "none") {
            preTag.style.display = "block";
        } else {
            preTag.style.display = "none";
        }
    }
    '''

    head.append(script)
    html.append(head)

    body = soup.new_tag("body")
    question_file_content = soup.new_tag("div")

    if "text" in dictionary.keys():
        for file in dictionary["text"]:
            file_container = soup.new_tag("div")

            text_file_path = os.path.join(source_dir, file)
            content = get_code_file_content(text_file_path)
            content['style'] = 'margin:0;'

            if file == "CMakeLists.txt":
                file_container['class'] = 'cmake'
                file_container['class'] += ' file'
                file_container['style'] = 'border: 1px solid rgb(100, 98, 99);'

                file_name_paragraph = soup.new_tag("p")
                file_name_paragraph['class'] = 'file-name'
                file_name_paragraph.string = file
                file_name_paragraph['style'] = 'margin:0; color:white;'
                file_name_paragraph['style'] += 'background-color: rgb(100, 98, 99);'

                file_container.append(file_name_paragraph)
                file_container.append(content)
                file_container['style'] += 'padding:0; margin: 10px; width:140ch;'
                question_file_content.append(file_container)

    if "headers" in dictionary.keys():
        for file in dictionary["headers"]:
            file_container = soup.new_tag("div")

            header_file_path = os.path.join(source_dir, file)
            content = get_code_file_content(header_file_path)
            content['style'] = 'margin:0;'

            file_container['class'] = 'header'
            file_container['class'] += ' file'
            file_container['style'] = 'border: 1px solid rgb(130, 27, 198);'

            file_name_paragraph = soup.new_tag("p")
            file_name_paragraph['class'] = 'file-name'
            file_name_paragraph.string = file
            file_name_paragraph['style'] = 'margin:0; color:white;'
            file_name_paragraph['style'] += 'background-color: rgb(130, 27, 198);'

            file_container.append(file_name_paragraph)
            file_container.append(content)
            file_container['style'] += 'padding:0; margin: 10px; width:140ch;'
            question_file_content.append(file_container)

    if "sources" in dictionary.keys():
        for file in dictionary["sources"]:
            file_container = soup.new_tag("div")

            src_file_path = os.path.join(source_dir, file)
            content = get_code_file_content(src_file_path)

            file_name_paragraph = soup.new_tag("p")
            file_name_paragraph['class'] = 'file-name'
            file_name_paragraph.string = file
            file_name_paragraph['style'] = 'margin:0; color:white;'

            if file == "main.cpp":
                file_container['class'] = 'main'
                file_container['style'] = 'border:1px solid rgb(144, 13, 13);'
                file_name_paragraph['style'] += 'background-color: rgb(144, 13, 13);'
            else:
                file_container['class'] = 'source'
                file_container['style'] = 'border:1px solid rgb(50, 50, 185);'
                file_name_paragraph['style'] += 'background-color: rgb(50, 50, 185);'

            file_container['class'] += ' file'

            content['style'] = 'margin:0;'


            file_container.append(file_name_paragraph)
            file_container.append(content)
            file_container['style'] += 'padding:0; margin: 10px; width:140ch;'
            question_file_content.append(file_container)

    if "md" in dictionary.keys():
        for file in dictionary["md"]:    
            md_file_path = os.path.join(source_dir, file)
            parse_readme(md_file_path, question_file_content)

    body.append(question_file_content)
    html.append(body)
    
    with open(html_file_path, "w") as html_file:
        html_file.write(html.prettify())


def create_question_hierarchy(parent_dir, dir_name, dictionary, question_path, cpp_sources_dir):
    if is_question(dictionary):
        question_path += ".html"
        directory_content = parent_dir.find('ul', class_='directory-content')
        # directory_content['style'] += 'display:none;'
        if directory_content:
            directory_content.append(create_question(dir_name, question_path))

        generate_question_html(question_path, cpp_sources_dir, dictionary)
    else:
        directory = create_directory(dir_name)

        if parent_dir['class'] == 'question-container':
            parent_dir.append(directory)
        else:
            directory_content = parent_dir.find('ul', class_='directory-content')
            directory_content.append(directory)
        
        for sub_dir_name in dictionary.keys():
            create_question_hierarchy(directory, sub_dir_name, dictionary[sub_dir_name], os.path.join(question_path, sub_dir_name), cpp_sources_dir)



def generate_html_files(cpp_sources_dir, resulting_html_structure_dir):
    html = soup.new_tag("html")
    head = soup.new_tag("head")
    script = soup.new_tag("script")
    script.string = '''
    function toggleDirectory(event)
    {
        const parentNode = event.target.parentNode;
        let directoryContent = parentNode.getElementsByClassName("directory-content")[0];

        if (directoryContent.style.display == "none") {
            directoryContent.style.display = "block";
        } else {
            directoryContent.style.display = "none";
        }
    }
    '''
    head.append(script)
    html.append(head)


    question_container = soup.new_tag("ul")
    question_container['class'] = 'question-container'
    question_container['style'] = 'margin-left:1em;'

    main_directories = SOURCES_STRUCTURE.keys()

    starting_path = resulting_html_structure_dir
    for dir_name in main_directories:
        question_path = os.path.join(starting_path, dir_name)
        create_question_hierarchy(question_container, dir_name, SOURCES_STRUCTURE[dir_name], question_path, cpp_sources_dir)

    body = soup.new_tag("body")
    body.append(question_container)
    html.append(body)

    return html


def save_html_file_content(question_container):
    with open("index.html", "w") as html_file:
        html_file.write(question_container.prettify())


def create_HTML_structure_for_cpp_projects(cpp_sources_dir, resulting_html_structure_dir):
    for root, dirs, files in os.walk(cpp_sources_dir, topdown=True):
        for name in files:
            file_path = os.path.join(root, name)
            rel_path = os.path.relpath(file_path, cpp_sources_dir)
            update_sources_structure(rel_path)

    question_container = generate_html_files(cpp_sources_dir, resulting_html_structure_dir)

    save_html_file_content(question_container)


if __name__ == "__main__":
    cpp_sources_dir = SRC_DIR
    resulting_html_structure_dir = HTML_DIR

    create_HTML_structure_for_cpp_projects(cpp_sources_dir, resulting_html_structure_dir)
