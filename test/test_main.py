"""
Test src.main.py
"""

from kivy.clock import Clock
import pytest
import os, sys

# Go into root dir to enable imports
ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../"

# Modify Python path to enable import custom modules in root dir.
sys.path.append(ROOT_DIR)

from src.main import Main  # Import your app class


error_message_dice_format = 'Bad entry ("{hint_text}"). Get `{text}`, Expected format "XDY+Z" (ex: 2 or 2d6 or 3D3+4) !'
error_message_int_format = 'Bad entry ("{hint_text}"). Get `{text}`, expected int !'

def test_wrong_inputs():
    """
    Test all fields: fill them with wrong message > test dialog box opens
    Idem filled with Ok message > test dialog box not opens
    """
    # 1/ Create an instance of the app
    # ---------------------------------
    app = Main()

    # Build the app's UI
    app.build()

    # 2/ Generate test plan
    # ---------------------------------
    # List all fields to test
    int_field_list_to_test = [app.field_nb_figs, app.field_s, app.field_ap, app.field_dmg, app.field_crits]  # contains int
    dice_format_fields_to_test = [app.sustain_hit, app.field_a, app.field_dmg]  # contains str like "2d6+1"

    # List to fill containing all tests to perform
    list_tests = []
    # ex: [("aaaaa", app.field_nb_figs, error_message_int_format)...]

    for f in int_field_list_to_test:
        list_tests += [("aaaaa", f, error_message_int_format)]  # Invalid input, dialog should appear
        list_tests += [("2", f, None)]  # Valid input, dialog should NOT appear

    for f in dice_format_fields_to_test:
        list_tests += [("aaaaa", f, error_message_dice_format)]  # Invalid input, dialog should appear

        # Valid input, dialog should NOT appear (test also lower, upper case)
        list_tests += [("2", f, None)]
        list_tests += [("2d6+1", f, None)]
        list_tests += [("d6+1", f, None)]
        list_tests += [("d3", f, None)]
        list_tests += [("2D6+1", f, None)]
        list_tests += [("D6+1", f, None)]
        list_tests += [("D3", f, None)]

    # 3/ Launch test plan
    # ---------------------------------
    @pytest.mark.parametrize("input_text, input_field, dialog_expected", list_tests)
    def _check_input(input_text, input_field, dialog_expected, app=app):
        """
        Launch app and test what appens if `input_field` is filled with `input_text`.
        If `dialog_expected` provided, check if MDDialog is opened with the message. Else, check no dialog open.
        """
        # Set the text in the MDTextField
        input_field.text = input_text

        # Simulate clicking the submit button (which triggers the validation)
        app.submit_button.dispatch('on_press')

        # Wait for the dialog to appear
        Clock.tick()

        # Check if the dialog is opened
        if dialog_expected != None:
            message_expected = dialog_expected.format(hint_text=input_field.hint_text, text=input_text)
            # ex: 'Bad entry ("NB figurines"). Expected int !'

            assert app.dialog is not None and app.dialog.open
            assert app.dialog.text == message_expected
        else:
            assert app.dialog is None or not app.dialog.open
