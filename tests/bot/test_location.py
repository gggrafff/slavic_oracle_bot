from telegram.ext._handlers.basehandler import BaseHandler
import pytest
from unittest.mock import AsyncMock, Mock

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.location import Location, MenuLocation, FuncLocation, Message


class TestLocation:
    """Test suite for Location class."""

    @pytest.fixture
    def basic_location(self) -> Location:
        """Create a basic Location instance."""
        return Location(
            name="Test Location",
            handlers=[],
            welcome_message=Message("Welcome to test location")
        )

    def test_location_initialization(self) -> None:
        """Test that Location initializes correctly."""
        location = Location(
            name="Test",
            handlers=[],
            welcome_message=Message("Hello")
        )

        assert location._name == "Test"
        assert location._welcome_message.text == "Hello"
        assert location._handlers == []
        assert location._is_implemented is True

    @pytest.mark.asyncio
    async def test_send_welcome_message(self, basic_location: Location) -> None:
        """Test that send_welcome_message sends correct message."""
        # Create mock update and context
        mock_update = Mock(spec=Update)
        mock_message = AsyncMock()
        mock_update.message = mock_message
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        # Call the method
        await basic_location.send_welcome_message(mock_update, mock_context)

        # Verify reply_text was called with correct parameters
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Welcome to test location" in str(call_args)

    @pytest.mark.asyncio
    async def test_send_welcome_message_no_message(self, basic_location: Location) -> None:
        """Test send_welcome_message when update has no message."""
        mock_update = Mock(spec=Update)
        mock_update.message = None
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        result = await basic_location.send_welcome_message(mock_update, mock_context)

        assert result is None

    def test_add_states(self, basic_location: Location) -> None:
        """Test that add_states adds location to states dict."""
        states: dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]] = {}

        basic_location.add_states(states)

        assert basic_location in states
        assert states[basic_location] == basic_location._handlers

    def test_add_states_does_not_duplicate(self, basic_location: Location) -> None:
        """Test that add_states doesn't add duplicate entries."""
        states: dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]] = {}

        basic_location.add_states(states)
        basic_location.add_states(states)

        # Should only have one entry
        assert len(states) == 1


class TestMenuLocation:
    """Test suite for MenuLocation class."""

    @pytest.fixture
    def menu_location(self) -> MenuLocation:
        """Create a MenuLocation instance."""
        return MenuLocation(
            name="Test Menu",
            welcome_message=Message("Choose an option")
        )

    def test_menu_location_initialization(self) -> None:
        """Test that MenuLocation initializes correctly."""
        menu = MenuLocation(name="Menu", welcome_message=Message("Welcome"))

        assert menu._name == "Menu"
        assert menu._welcome_message.text == "Welcome"
        assert menu._handlers == []
        assert menu._is_implemented is False  # Default for MenuLocation

    def test_menu_location_str_representation(self, menu_location: MenuLocation) -> None:
        """Test MenuLocation string representation."""
        assert str(menu_location) == 'Location "Test Menu"'

    def test_add_children_buttons_sets_children(self, menu_location: MenuLocation) -> None:
        """Test that add_children_buttons sets children correctly."""
        child1 = MenuLocation(name="Child 1", welcome_message=Message("Child 1"))
        child2 = MenuLocation(name="Child 2", welcome_message=Message("Child 2"))
        child1._is_implemented = True
        child2._is_implemented = True

        menu_location.add_children_buttons([child1, child2])

        assert menu_location._children == [child1, child2]
        assert len(menu_location._handlers) > 0

    def test_add_children_buttons_with_custom_names(self, menu_location: MenuLocation) -> None:
        """Test add_children_buttons with custom button names."""
        child1 = MenuLocation(name="Child 1", welcome_message=Message("Child 1"))
        child1._is_implemented = True

        menu_location.add_children_buttons([child1], children_names=["Custom Name"])

        # Check that keyboard was created
        assert isinstance(menu_location._keyboard, ReplyKeyboardMarkup)

    def test_add_children_buttons_marks_unimplemented(self, menu_location: MenuLocation) -> None:
        """Test that unimplemented children are marked with (soon)."""
        child = MenuLocation(name="Child", welcome_message=Message("Child"))
        child._is_implemented = False

        menu_location.add_children_buttons([child])

        # Parent should also be unimplemented if all children are
        assert menu_location._is_implemented is False

    def test_get_button_names(self, menu_location: MenuLocation) -> None:
        """Test _get_button_names extracts button names correctly."""
        child = MenuLocation(name="Child", welcome_message=Message("Child"))
        child._is_implemented = True
        menu_location.add_children_buttons([child])

        button_names = menu_location._get_button_names()

        assert isinstance(button_names, list)
        assert len(button_names) > 0

    def test_get_button_names_empty_keyboard(self, menu_location: MenuLocation) -> None:
        """Test _get_button_names with no keyboard."""
        button_names = menu_location._get_button_names()

        assert button_names == []

    def test_add_back_buttons(self, menu_location: MenuLocation) -> None:
        """Test that add_back_buttons adds back navigation."""
        # First add children buttons
        child = MenuLocation(name="Child", welcome_message=Message("Child"))
        child._is_implemented = True
        menu_location.add_children_buttons([child])

        # Then add back button
        parent = MenuLocation(name="Parent", welcome_message=Message("Parent"))
        menu_location.add_back_buttons([parent])

        button_names = menu_location._get_button_names()
        assert any("Back to Parent" in name for name in button_names)

    def test_add_back_buttons_before_children_logs_error(self, menu_location: MenuLocation) -> None:
        """Test that add_back_buttons logs error if called before children."""
        parent = MenuLocation(name="Parent", welcome_message=Message("Parent"))

        # Should not crash, but should log error
        menu_location.add_back_buttons([parent])

        # Handlers should still be empty
        assert menu_location._handlers == []


class TestFuncLocation:
    """Test suite for FuncLocation class."""

    @pytest.fixture
    def func_location(self) -> FuncLocation:
        """Create a FuncLocation instance."""
        def text_processor(text: str) -> str:
            return f"Processed: {text}"

        return FuncLocation(
            name="Func Test",
            text_func=text_processor,
            welcome_message=Message("Enter data")
        )

    def test_func_location_initialization(self) -> None:
        """Test that FuncLocation initializes correctly."""
        func_loc = FuncLocation(name="Test", welcome_message=Message("Hello"))

        assert func_loc._name == "Test"
        assert func_loc._welcome_message.text == "Hello"
        assert func_loc._redirect is None

    def test_func_location_str_representation(self, func_location: FuncLocation) -> None:
        """Test FuncLocation string representation."""
        assert str(func_location) == 'Location "Func Test"'

    def test_set_redirect(self, func_location: FuncLocation) -> None:
        """Test that set_redirect sets the redirect location."""
        redirect_loc = MenuLocation(name="Redirect", welcome_message=Message("Redirected"))

        func_location.set_redirect(redirect_loc)

        assert func_location._redirect == redirect_loc

    def test_prepare_handler_creates_handlers(self, func_location: FuncLocation) -> None:
        """Test that prepare_handler creates message handlers."""
        redirect_loc = MenuLocation(name="Redirect", welcome_message=Message("Redirected"))
        func_location.set_redirect(redirect_loc)

        # Before prepare_handler
        assert func_location._handlers == []

        func_location.prepare_handler()

        # After prepare_handler
        assert len(func_location._handlers) > 0

    @pytest.mark.asyncio
    async def test_func_location_handler_processes_text(self, func_location: FuncLocation) -> None:
        """Test that FuncLocation handler processes text correctly."""
        redirect_loc = MenuLocation(name="Redirect", welcome_message=Message("Redirected"))
        func_location.set_redirect(redirect_loc)
        func_location.prepare_handler()

        # Create mock update with message
        mock_update = Mock(spec=Update)
        mock_message = AsyncMock()
        mock_message.text = "test input"
        mock_update.message = mock_message
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        # Get the handler and call it
        handler = func_location._handlers[0].callback
        result = await handler(mock_update, mock_context)

        # Verify the text was processed (check first call, not last)
        # Handler calls reply_text twice: once for processed text, once for redirect welcome message
        assert mock_message.reply_text.call_count == 2
        first_call_args = str(mock_message.reply_text.call_args_list[0])
        assert "Processed:" in first_call_args

        # Verify redirect
        assert result == redirect_loc
