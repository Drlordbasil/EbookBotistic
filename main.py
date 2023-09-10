import os
import random
import string
import imgaug as ia
import imgaug.augmenters as iaa
from PIL import Image
from ebooklib import epub


class EbookGenerator:
    def __init__(self, model_list):
        self.model_list = model_list

    def generate_ebook(self, title, content):
        ebook = epub.EpubBook()
        ebook.set_title(title)

        for model in self.model_list:
            model_output = model.generate_output()
            ebook.add_item(model_output)

        ebook.toc = (
            epub.Link('title.xhtml', 'Introduction', 'intro'),
            (
                epub.Section('Models'),
                tuple(model.get_nav_element() for model in self.model_list)
            )
        )

        ebook.add_item(epub.EpubNcx())
        ebook.add_item(epub.EpubNav())

        ebook.spine = ['nav'] + [model.get_spine_element()
                                 for model in self.model_list]

        filename = self._save_ebook_file(ebook)
        return filename

    def _save_ebook_file(self, ebook):
        filename = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=8)) + '.epub'
        epub.write_epub(filename, ebook, {})
        return filename


class PhotoGenerator:
    def __init__(self, model_list):
        self.model_list = model_list

    def generate_photo(self):
        ia.seed(1)
        image = Image.open('input_image.jpg')

        for model in self.model_list:
            image = model.apply_augmentation(image)

        filename = self._save_photo(image)
        return filename

    def _save_photo(self, image):
        filename = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=8)) + '.jpg'
        image.save(filename)
        return filename


class EpubModel:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def generate_output(self):
        ebook_html = f'<html><body><h1>{self.title}</h1><p>{self.content}</p></body></html>'
        ebook_item = epub.EpubHtml(
            title=self.title, file_name=f'{self.title}.xhtml', content=ebook_html)
        return ebook_item

    def get_nav_element(self):
        return epub.Link(f'{self.title}.xhtml', self.title, f'{self.title.lower()}')

    def get_spine_element(self):
        return epub.Item(f'{self.title}.xhtml')


class PhotoModel:
    def __init__(self, augmentation_name):
        self.augmentation_name = augmentation_name

    def apply_augmentation(self, image):
        if self.augmentation_name == 'rotate':
            return iaa.rotate(image, angle=45)
        elif self.augmentation_name == 'flip':
            return iaa.flip(image)
        elif self.augmentation_name == 'contrast':
            return iaa.contrast_normalize(image)
        else:
            return image


class EbookPhotoGenerator:
    def __init__(self, ebook_model_list, photo_model_list):
        self.ebook_generator = EbookGenerator(ebook_model_list)
        self.photo_generator = PhotoGenerator(photo_model_list)

    def generate_ebook_and_photo(self, ebook_title, ebook_content):
        ebook_filename = self.ebook_generator.generate_ebook(
            ebook_title, ebook_content)
        photo_filename = self.photo_generator.generate_photo()

        return ebook_filename, photo_filename


if __name__ == '__main__':
    ebook_models = [
        EpubModel('Chapter 1', 'Lorem ipsum dolor sit amet'),
        EpubModel('Chapter 2', 'Consectetur adipiscing elit'),
        EpubModel(
            'Chapter 3', 'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua')
    ]

    photo_models = [
        PhotoModel('rotate'),
        PhotoModel('flip'),
        PhotoModel('contrast')
    ]

    generator = EbookPhotoGenerator(ebook_models, photo_models)
    generated_ebook, generated_photo = generator.generate_ebook_and_photo(
        'My Ebook', 'This is the content of my ebook')

    print(f"Ebook generated: {generated_ebook}")
    print(f"Photo generated: {generated_photo}")
