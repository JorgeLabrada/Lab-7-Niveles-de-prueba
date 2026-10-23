import book 
import pytest
import user
import library

@pytest.mark.unit
def test_borrow_book():
    book1=book.Book('El alquimista','Paulo Coehlo',1967,'ISBN0001')
    assert book1.title == 'El alquimista'
    book1.borrow()
    assert book1.borrowed==True

@pytest.mark.unit
def test_re_borrow_book():
    book1=book.Book('El alquimista','Paulo Coehlo',1967,'ISBN0001')
    assert book1.title == 'El alquimista'
    book1.borrow()
    assert book1.borrowed==True
    with pytest.raises(ValueError,match="The book is already borrowed"):
        book1.borrow()

@pytest.mark.unit
def test_return_book():
    book1=book.Book('El alquimista','Paulo Coehlo',1967,'ISBN0001')
    assert book1.title == 'El alquimista'
    book1.borrow()
    assert book1.borrowed==True
    book1.return_book()
    assert book1.borrowed==False

@pytest.mark.system
def test_library_borrow():
    book1=book.Book('El alquimista','Paulo Coehlo',1967,'ISBN0001')
    miguel = user.User('Miguel','ID0001')
    lib = library.Library()
    lib.add_book(book1)
    assert lib.books[0].title == 'El alquimista'
    lib.add_user(miguel)
    #corroborar que se agrego 
    lib.borrow_book('ID0001','ISBN0001')
    assert book1.borrowed==True


@pytest.fixture
def library_init():
    book1=book.Book('El alquimista','Paulo Coehlo',1967,'ISBN0001')
    miguel = user.User('Miguel','ID0001')
    lib = library.Library()
    lib.add_book(book1)
    lib.add_user(miguel)
    return lib

@pytest.mark.wip
def test_library_fixture(library_init):
    lib = library_init
    #corroborar que se agrego 
    lib.borrow_book('ID0001','ISBN0001')
    assert lib.books[0].borrowed==True

# ----------------adicionales 

# isbn que no existen
@pytest.mark.unit
@pytest.mark.parametrize("isbn", ["ISBN9999", "", "isbn0001", None])
def test_find_book_not_found(library_init, isbn):
    with pytest.raises(ValueError, match="Book not found"):
        library_init.borrow_book('ID0001', isbn)


# 2. no loaneo
@pytest.mark.integration
def test_loans_disabled(library_init, monkeypatch, capsys):
    monkeypatch.setitem(library.settings, "loans_enabled", False)
    library_init.borrow_book('ID0001', 'ISBN0001')
    salida = capsys.readouterr().out
    assert "Loans are disabled" in salida
    assert library_init.books[0].borrowed == False


# 3 prestar devolver y registrar en el historial
@pytest.mark.integration
def test_borrow_and_return_history(library_init):
    lib = library_init
    lib.borrow_book('ID0001', 'ISBN0001')
    lib.return_book('ID0001', 'ISBN0001')
    assert lib.books[0].borrowed == False
    assert len(lib.users[0].get_history()) == 2


# 4. skipeo si no hay usuarios
@pytest.mark.unit
def test_user_not_found(library_init):
    if not library_init.users:
        pytest.skip("No hay usuarios registrados")
    with pytest.raises(ValueError, match="User not found"):
        library_init.return_book('ID9999', 'ISBN0001')


# 5. xfail si hay ralta de ortografia
@pytest.mark.unit
@pytest.mark.xfail(reason="Bug conocido: user.py escribe 'Borrwed' en lugar de 'Borrowed'")
def test_history_text(library_init):
    library_init.borrow_book('ID0001', 'ISBN0001')
    assert library_init.users[0].get_history() == ["Borrowed: El alquimista"]
