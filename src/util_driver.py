from selenium import webdriver
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup


def full_screenshot(driver, filename=''):
    # initiate value
    save_path = filename + '.png' if filename[-4::] != '.png' else filename
    img_li = []  # to store image fragment
    offset = 0  # where to start

    # js to get height
    height = driver.execute_script('return Math.max('
                                   'document.documentElement.clientHeight, window.innerHeight);')

    # js to get the maximum scroll height
    # Ref--> https://stackoverflow.com/questions/17688595/finding-the-maximum-scroll-position-of-a-page
    max_window_height = driver.execute_script('return Math.max('
                                              'document.body.scrollHeight, '
                                              'document.body.offsetHeight, '
                                              'document.documentElement.clientHeight, '
                                              'document.documentElement.scrollHeight, '
                                              'document.documentElement.offsetHeight);')

    # looping from top to bottom, append to img list
    # Ref--> https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    while offset < max_window_height:

        # Scroll to height
        driver.execute_script(f'window.scrollTo(0, {offset});')
        img = Image.open(BytesIO((driver.get_screenshot_as_png())))
        img_li.append(img)
        offset += height

    # Stitch image into one
    # crop the last image
    if offset > max_window_height:
        size = img_li[-1].size
        area = (0, (offset - max_window_height) *
                size[1] / height, size[0], size[1])
        crop = img_li[-1].crop(area)
        img_li.pop()
        img_li.append(crop)
    # Set up the full screen frame
    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])

    img_frame = Image.new('RGB', (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    if not filename:
        return img_frame
    else:
        img_frame.save(save_path)


def gather_info(driver):
    source = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(source)

    content_li = soup.find_all('div', {'class': 'row'})
    info_set = {}

    for item in content_li:
        children = item.findChildren('div', {'class': 'section-content'})
        member = [child.text for child in children]
        try:
            title = member[0]
            info = " ".join(member[1::])
            info_set[title] = info
        except IndexError:
            pass


def element_screenshot(driver, filename=''):
    """
    :param driver: is the name of the webdriver
    :param filename: is the absolute path of the file
    :return: multiple image files of website sections
    """
    import re
    # initiate value
    save_path = filename + '.png' if filename[-4::] != '.png' else filename
    save_name = re.split('(.png)', save_path)
    url = driver.current_url
    if url.__contains__('https://www.'):
        url_name = url.split('https://www.')[1]
        url_name = url_name.replace('/', '+')
    else:
        url_name = url.split('http://www.')[1]
        url_name = url_name.replace('/', '+')

    # get all element location
    sections = driver.find_elements_by_tag_name('section')
    # TODO other tag, class type?

    # filter out non visible element
    visible_section = [
        section for section in sections if section.size['height'] > 10]
    img_frame = full_screenshot(driver)

    # extract section image in full screenshot
    for i, section in enumerate(visible_section):
        size = section.size
        axis = section.location
        class_name = section.get_attribute('class')
        box = (
            axis['x'], axis['y'],  # bottom left x y
            axis['x'] + size['width'], axis['y'] + size['height'])  # top right x y
        img = img_frame.crop(box)
        img.save('{}{}_#{}_{}_{}'.format(
            save_name[0], url_name, class_name, i, save_name[1]))
