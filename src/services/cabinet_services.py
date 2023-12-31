from core.constants import ErrorTitle
from core.generics import err, ok, runDomainService, AppErrors
from repository.model.cabinet import BoardSchema
from repository.protocols.cabinet_repo_meta import CabinetRepo
from domains.cabinet import Cabinet, CabinetPatcher
from schemas.cabinet import (
    CabinetBulkResult,
    CabinetRemovalOutput,
    CreateCabinet,
    CabinetResult,
    PatchCabinetInput,
    PatchCabinetOutput,
)


class CabinetService:
    repo: CabinetRepo

    def __init__(self, repo: CabinetRepo):
        self.repo = repo

    def getAllCabinets(self, user_id: str):
        items = self.repo.get_all_by_user_id(user_id)
        conv = lambda Cdata: CabinetResult(**Cdata.model_dump())
        return ok(CabinetBulkResult(cabinets=list(map(conv, items))))

    def getOneCabinets(self, cabinet_id: str):
        item = self.repo.get(cabinet_id)
        if item is None:
            return err(
                "Cabinet with the id {} is not found".format(cabinet_id),
                AppErrors.EMPTY,
            )

        conv = lambda Cdata: CabinetResult(**Cdata.model_dump())
        return ok(conv(item))

    def appendBoardToCabinet(self, cabinet_id: str, board: BoardSchema):
        fetched = self.repo.get(cabinet_id)
        board_id = board.board_id
        entity = self.repo.db_to_entity(fetched)

        if entity is None:
            return err("Cabinet not found", AppErrors.EMPTY)

        entity.appendBoardRef(board_id)
        dbData = self.repo.entity_to_db(entity, to_dict=True)
        self.repo.update(cabinet_id, dbData)

        return ok(CabinetResult(**entity.model_dump()), "board appended")

    def createCabinet(self, cabinet_data: CreateCabinet):
        newCabinet = lambda: Cabinet.create(
            name=cabinet_data.name, author=cabinet_data.authorId
        )

        domainRes = newCabinet()
        # domainRes = runDomainService(newCabinet);
        dto = self.repo.entity_to_db(domainRes, to_dict=True)

        self.repo.add(**dto)

        res = CabinetResult(**domainRes.model_dump())
        return ok(res)

    def deleteCabinet(self, cabinet_id: str):
        try:
            _db_res = self.repo.remove(cabinet_id)
        except Exception as e:
            return err(str(e), AppErrors.EMPTY)
        return ok(CabinetRemovalOutput(cabinetId=cabinet_id))

    def updateCabinet(self, cabinet_id: str, patchDetail: PatchCabinetInput):
        try:
            _res = self.repo.update(
                cabinet_id, CabinetPatcher(**patchDetail.model_dump())
            )
            if not _res:
                return err(
                    "Cabinet with id of {} is not found".format(cabinet_id),
                    AppErrors.EMPTY,
                    title=ErrorTitle.NOT_FOUND,
                )

        except Exception as e:
            return err(str(e), AppErrors.EMPTY)
        return ok(
            PatchCabinetOutput(modified=True, id=cabinet_id, attributes=patchDetail)
        )

    # def retrieveCabinet(self):
    #     self.repo.get_all_by_user_id
    #     pass
