from core.generics import ServiceDTO, err, ok, runDomainService, AppErrors
from repository.model.cabinet import CabinetSchema
from repository.protocols.board_repo_meta import BoardRepo
from domains.board import Board, BoardPatcher
from repository.protocols.cabinet_repo_meta import CabinetRepo
from schemas.board import (
    BoardBulkResult,
    BoardResult,
    CreateBoardInput,
    PatchBoardInput,
    PatchBoardOutput,
    RemoveBoardOutput,
)
from services.cabinet_services import CabinetService


class BoardService:
    repo: BoardRepo
    cabinetService: CabinetService

    def __init__(self, repo: BoardRepo, parentService: CabinetService):
        self.repo = repo
        self.cabinet = parentService

    def createBoard(self, board_data: CreateBoardInput) -> ServiceDTO:
        makeDomainObject = lambda: Board.create(
            name=board_data.name, topic=board_data.topic
        )
        entity = makeDomainObject()

        # entity = runDomainService(makeDomainObject)
        dbSchema = self.repo.entity_to_db(board_data.cabinetId, entity, to_dict=True)
        self.repo.add(**dbSchema)
        # self.cabinet.appendBoardToCabinet(board_data.cabinetId, dbSchema)

        return ok(
            BoardResult(**entity.model_dump()),
            "successfully create a new board!",
        )

    def getAllBoard(self, cabinet_id: str):
        cid = cabinet_id
        # self.repo.add(self.repo.entity_to_db(fetcher.cabinet_id, entity, to_dict=True))
        db_result = self.cabinet.repo.get(cid, lazy_options={"queryField": "boards"})
        if db_result is None:
            return err(
                "Cabinet with the id {} is not found".format(cid),
                AppErrors.EMPTY,
            )

        board_db_to_entity = lambda board_db_data: self.repo.db_to_entity(board_db_data)
        boards = map(board_db_to_entity, db_result)
        conv = lambda data: BoardResult(**data.model_dump())

        boardList = list(map(conv, boards))
        return ok(
            BoardBulkResult(boards=boardList, count=len(boardList)),
            "successfully fetch all boards",
        )

    def deleteBoard(self, boardId: str):
        db_result = self.repo.remove(boardId)
        if db_result is False:
            return err(
                "Board with the id {} is not found!".format(boardId),
                AppErrors.EMPTY,
            )
        return ok(RemoveBoardOutput(removed=1))

    def patchBoard(self, boardId: str, patches: PatchBoardInput):
        db_result = self.repo.update(boardId, patches)
        if db_result is False:
            return err(
                "Board with the id {} is not found!".format(boardId),
                AppErrors.EMPTY,
            )
        return ok(
            PatchBoardOutput(modified=db_result, boardId=boardId, attributes=patches)
        )
