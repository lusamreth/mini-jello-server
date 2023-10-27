import datetime
from sqlalchemy import DateTime
from core.base_repo import BaseRepository
from domains.cabinet import Board, Cabinet
from repository.adapters.base_sql_repo import BaseRepo
from repository.model.cabinet import BoardSchema, CabinetSchema
from ..protocols.cabinet_repo_meta import CabinetRepo

class CabinetRepoImpl(BaseRepo[CabinetSchema],CabinetRepo):
    def __init__(self, session_factory):
        super().__init__(
            model=CabinetSchema,
            session_factory=session_factory,
            primary_key_identifier="cabinet_id",
        )

    def get_all_by_topic(self, topic: str):
        with self.session_factory() as session:
            bulks = session.query(self.model).filter(
                    self.model.topic == topic).all()
            return bulks

    def get_all_by_user_id(self,user_id):
        with self.session_factory() as session:
            bulks = session.query(self.model).filter(
                    self.model.author == user_id).all()
            return bulks

    def db_to_entity(self, db_data : CabinetSchema | None) -> Cabinet | None:
        def schemaConverter(board_schema: BoardSchema) -> str:
            return board_schema.board_id

        if db_data is not None: 
            return Cabinet(
                cabinetId=db_data.cabinet_id,
                name=db_data.name,
                author=db_data.author,
                # boardRefs=list(map(schemaConverter,db_data.board_id_refs)),
                boardRefs=list(map(schemaConverter,[])),
                # createdOn=float(db_data.created_on)
                createdOn=float(1)
            )
            
    def entity_to_db(self, cabinet_domain: Cabinet | None) -> CabinetSchema | None:
        if cabinet_domain is not None: 
            cd = cabinet_domain
            return CabinetSchema(cabinet_id=cd.cabinetId, 
                                 name=cd.name,
                                 author=cabinet_domain.author,
                                 board_id_refs=[],
                                 )
    
