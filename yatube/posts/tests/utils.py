from django.core.files.uploadedfile import SimpleUploadedFile


def get_image(file_name, content_type):
    return SimpleUploadedFile(
        file_name, (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        ),
        content_type
    )


def posts_assertEqual(self, post1, post2):
    self.assertEqual(post1, post2)
    self.assertEqual(post1.text, post2.text)
    self.assertEqual(post1.author, post2.author)
    self.assertEqual(post1.group, post2.group)
    self.assertEqual(post1.image, post2.image)
