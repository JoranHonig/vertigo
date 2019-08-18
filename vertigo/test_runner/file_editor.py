from typing import Tuple


class FileEditor:
    @staticmethod
    def edit(target_file_name: str, edit_location: Tuple[int, int, int], replacement: str) -> None:
        """
        Rewrites the edit location in the target file with the replacement
        :param target_file_name: Name of the file to apply the rewrite to
        :param edit_location: Location to rewrite
        :param replacement: Replacement for location
        """
        if edit_location[0] <= 0:
            raise ValueError("Cannot edit in the negative space")

        with open(target_file_name, 'r') as file:
            content = file.read()

        with open(target_file_name, 'w') as file:
            new_content = content[:edit_location[0]] \
                          + replacement + \
                          content[edit_location[0] + edit_location[1]:]
            file.write(new_content)
