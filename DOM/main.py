from auth import AuthScreen
from logger import logger
from menu import MenuScreen
from network import NetworkClient
from start_app import StartAppScreen
from utils import FinishStatus


@logger.catch
def main():
    network_client = NetworkClient()
    match StartAppScreen(network_client).exec():
        case FinishStatus.ok:
            MenuScreen().exec()
        case FinishStatus.auth_failed:
            if AuthScreen(network_client, FinishStatus.fail_msg).exec() == FinishStatus.ok:
                MenuScreen().exec()
