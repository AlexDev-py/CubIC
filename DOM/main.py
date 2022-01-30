from auth import AuthScreen
from game_client import GameClientScreen
from logger import logger
from menu import MenuScreen
from network import NetworkClient
from start_app import StartAppScreen
from utils import FinishStatus


def menu_screen(network_client: NetworkClient) -> None:
    if MenuScreen(network_client).exec() == FinishStatus.enter_game:
        game_client_screen(network_client)


def game_client_screen(network_client: NetworkClient) -> None:
    if GameClientScreen(network_client).exec() == FinishStatus.exit_game:
        menu_screen(network_client)


@logger.catch
def main():
    network_client = NetworkClient()
    match StartAppScreen(network_client).exec():
        case FinishStatus.ok:
            menu_screen(network_client)
        case FinishStatus.auth_failed:
            if AuthScreen(network_client, FinishStatus.fail_msg).exec() == FinishStatus.ok:
                menu_screen(network_client)
