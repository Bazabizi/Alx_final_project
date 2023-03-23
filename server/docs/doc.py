"""Gets and prints the spreadsheet's header columns

Args:
    file_loc (str): The file location of the spreadsheet
    print_cols (bool): A flag used to print the columns to the console
        (default is False)

Returns:
    list: a list of strings representing the header columns
"""

from flask import Blueprint, render_template, redirect, url_for

doc_bp = Blueprint('doc_bp', __name__,
                   static_folder='static',
                   template_folder='templates')


@doc_bp.route('/')
def doc():
    return render_template(['doc.html', 'home.html'])
