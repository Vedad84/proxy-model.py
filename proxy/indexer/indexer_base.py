import time
import logging

from ..common_neon.solana_tx import SolCommit
from ..common_neon.config import Config
from ..common_neon.solana_interactor import SolInteractor


LOG = logging.getLogger(__name__)


class IndexerBase:
    def __init__(self, config: Config, solana: SolInteractor, last_slot: int):
        self._solana = solana
        self._config = config

        start_slot = self._get_start_slot(last_slot)
        first_slot = solana.get_first_available_block()
        self._start_slot = max(start_slot, first_slot)
        LOG.info(f'FIRST_AVAILABLE_SLOT={first_slot}: started the receipt slot from {self._start_slot}')

    def _get_start_slot(self, last_known_slot: int) -> int:
        """
        This function allow to skip some part of history.
        - LATEST - start from the last block slot from Solana
        - CONTINUE - continue from the last parsed slot of from latest
        - NUMBER - first start from the number, then continue from last parsed slot
        """
        last_known_slot = 0 if not isinstance(last_known_slot, int) else last_known_slot
        latest_slot = self._solana.get_block_slot(SolCommit.Finalized)
        start_int_slot = 0

        start_slot = self._config.start_slot
        LOG.info(f'Starting the receipt slot with LATEST_KNOWN_SLOT={last_known_slot} and START_SLOT={start_slot}')

        if start_slot not in {'CONTINUE', 'LATEST'}:
            try:
                start_int_slot = min(int(start_slot), latest_slot)
            except (Exception,):
                start_int_slot = 0

        if start_slot == 'CONTINUE':
            if last_known_slot > 0:
                LOG.info(f'START_SLOT={start_slot}: started the receipt slot from previous run {last_known_slot}')
                return last_known_slot
            else:
                LOG.info(f'START_SLOT={start_slot}: forced the receipt slot from the latest Solana slot')
                start_slot = 'LATEST'

        if start_slot == 'LATEST':
            LOG.info(f'START_SLOT={start_slot}: started the receipt slot from the latest Solana slot {latest_slot}')
            return latest_slot

        if start_int_slot < last_known_slot:
            LOG.info(f'START_SLOT={start_slot}: started the receipt slot from previous run {last_known_slot}')
            return last_known_slot

        LOG.info(f'START_SLOT={start_slot}: started the receipt slot from {start_int_slot}')
        return start_int_slot

    def run(self):
        check_sec = float(self._config.indexer_check_msec) / 1000
        while True:
            try:
                self.process_functions()
            except BaseException as exc:
                LOG.warning('Exception on transactions processing.', exc_info=exc)
            time.sleep(check_sec)

    def process_functions(self) -> None:
        pass
