import json
from fastapi import FastAPI
import uvicorn
import random
import pandas as pd
import json 
import xml
from business_object.regle_generation.typ import Type
from business_object.regle_generation.modality import Modality
from business_object.regle_generation.meta_type import Meta_type
from business_object.generation_donnee import Generation_donnee
from business_object.impor.import_json import IMPORTJSON
from business_object.export.export import Export
from business_object.export.export_to_xml import Export_to_xml
from business_object.export.export_to_csv import Export_to_csv
from business_object.export.export_to_json import Export_to_json
from factory.data_factory import DataFactory
from factory.meta_factory import MetaFactory
from factory.modality_factory import ModalityFactory
from factory.typ_factory import TypeFactory
from dao.data_dao import DataDao
from dao.db_connection import DBConnection
from dao.meta_dao import MetaDao
from dao.modality_dao import ModalityDao
from dao.typ_dao import TypeDao



tags_metadata = [{"name" : "Type"},{"name" : "Modality"},{"name": "Import"},
                 {"name" : "Meta-Type"},{"name" : "Génération et sauvegarde"},
                 {"name" : "Export"},  
                 {"name": "Modality DAO"}, {"name": "Type DAO"}, {"name": "Metatype DAO"}, {"name": "Donnees DAO"}]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/get_dict_type", tags = ["Type"])
async def get_type():
    return Type.dict_type

@app.put("/add_type/", tags = ["Type"])
async def add_type(nom : str, tx_remplissage : float):
    t = Type(tx_remplissage, nom)
    return t.add_type()

@app.delete("/delete_type/", tags = ["Type"])
async def delete_type(nom : str):
    return Type.delete_type(nom)

@app.get("/get_dict_modality", tags = ["Modality"])
async def get_modality():
    return Modality.dict_modality

@app.put("/add_modality/", tags = ["Modality"])
async def add_modality(nom_type : str, proba_apparition : float, value):
    m = Modality(nom_type, proba_apparition, value)
    return m.add_modality()

@app.delete("/delete_modality", tags = ["Modality"])
async def delete_modality(nom_type : str, value):
    return Modality.delete_modality(nom_type, value)

@app.put("/import_json/", tags = ["Import"])
async def import_json(chemin : "str"):
    imp = IMPORTJSON(chemin)
    return imp.import_dict()

@app.get("/get_dict_meta_type", tags = ["Meta-Type"])
async def get_meta_type():
    return Meta_type.dict_meta_type

@app.put("/add_meta_type/", tags = ["Meta-Type"])
async def add_meta_type(nom : str, list_type : list):
    mt = Meta_type(nom, list_type)
    return mt.add_meta_type()

@app.delete("/delete_meta_type/", tags = ["Meta-Type"])
async def delete_meta_type(nom_meta_type : str):
    return Meta_type.delete_meta_type(nom_meta_type)


@app.put("/generation_de_donnee/", tags = ["Génération et sauvegarde"])
async def generation_donnee(Nb : int, meta_type ):
    gd = Generation_donnee(Nb, meta_type)
    return gd.generer_jeu_donnee()

@app.get("/get_dict_jeu_donnee/", tags = ["Génération et sauvegarde"])
async def get_all_data():
    dat = Generation_donnee.jeu_donnee
    return dat

@app.delete("/reinitialiser_base_de_donnees", tags = ["Génération et sauvegarde"])
async def delete_all_tables():
    ModalityDao().delete_all_modality()
    TypeDao().delete_all_type()
    MetaDao().delete_all_meta_type()
    DataDao().delete_all_data()

@app.put("/sauvegarder_en_base_de_donnees/", tags = ["Génération et sauvegarde"])
async def save_data_dao():
    donnee = DataDao()
    meta = MetaDao()
    typ = TypeDao()
    modalite = ModalityDao()
    meta.save_meta(Meta_type(Generation_donnee.meta_type1[-1], Meta_type.dict_meta_type[Generation_donnee.meta_type1[-1]]))
    for elt in Meta_type.dict_meta_type[Generation_donnee.meta_type1[-1]] : 
        typ.save_type(Type(Type.dict_type[elt]["remplissage"], elt))
    for mod in Modality.dict_modality :
        modalite.save_modality(Modality(Modality.dict_modality[mod]["type"], Modality.dict_modality[mod]["proba d'apparition"], Modality.dict_modality[mod]["value"]))
    modalite.delete_doublons()
    typ.delete_doublons()
    meta.delete_doublons()
    donnee.save_data(Generation_donnee.tailles[-1], Generation_donnee.meta_type1[-1], Generation_donnee.jeu_donnee)

@app.get("/export/", tags = ["Export"])
async def export(chemin : str, name : str):
    return None

@app.get("/export_donnees_to_json/", tags = ["Export"])
async def export_json(chemin : str , name : str):
    x = Export_to_json(chemin, name)
    dic = json.dumps(Generation_donnee.jeu_donnee)
    return x.export(dic)

@app.get("/export_donnees_to_xml/", tags = ["Export"])
async def export_xml(chemin : str , name : str):
    x = Export_to_xml(chemin, name)
    dic = json.dumps(Generation_donnee.jeu_donnee)
    return x.export(dic)

@app.get("/export_donnees_to_csv/", tags = ["Export"])
async def export_csv(chemin : str , name : str):
    c = Export_to_csv(chemin, name)
    dic = json.dumps(Generation_donnee.jeu_donnee)
    return c.export(dic)

@app.get("/find_all_modality/", tags = ["Modality DAO"])
async def find_modalities():
    modalite = ModalityDao()
    return modalite.find_all_modality()

@app.get("/find_modality_by_id/", tags = ["Modality DAO"])
async def find_mod_id(id : int):
    try :
        modalite = ModalityDao()
        return modalite.find_modality_by_id(id)
    except:
        raise Exception("Aucune modalité ne correspond à cet id")

@app.get("/find_modality_by_modality/",  tags = ["Modality DAO"])
async def find_mod_mod(nom_mod, proba, value, limit : int = None):
    modalite = Modality(nom_mod, proba, value)
    return modalite.find_modality(Modality(nom_mod, proba, value), limit = limit)

@app.put("/update_modality_by_id/", tags = ["Modality DAO"])
async def update_modality_by_id(id, new_type, new_value, new_proba_apparition):
    try :
        mod = ModalityDao()
        mod.update_modality_by_id(id, new_type, new_value, new_proba_apparition)
    except:
        raise Exception("Aucune modalité ne correspond")
    
@app.delete("/delete_modality_by_id/",  tags = ["Modality DAO"])
async def delete_mod_id(id) :
    mod = ModalityDao()
    mod.delete_modality_by_id(id)

@app.delete("/delete_modality_by_type/",  tags = ["Modality DAO"])
async def delete_mod_typ(nom_type) :
    mod = ModalityDao()
    mod.delete_modality_by_type(nom_type)

@app.delete("/delete_modality_by_mod/",  tags = ["Modality DAO"])
async def delete_mod_mod(nom_type, proba_apparition, value) :
    mod1 = Modality(nom_type, proba_apparition, value)
    mod = ModalityDao()
    mod.delete_modality_by_mod(mod1)

@app.delete("/delete_all_modality/", tags = ["Modality DAO"])
async def delete_all_mod():
    mod = ModalityDao()
    mod.delete_all_modality()

@app.get("/find_all_type/",  tags = ["Type DAO"])
async def find_types():
    typ = TypeDao()
    return typ.find_all_type()

@app.get("/find_type_by_id/", tags = ["Type DAO"])
async def find_typ_id(id : int):
    try:
        typ = TypeDao()
        return typ.find_type_by_id(id)
    except:
        raise Exception("Aucun type ne correspond à cet id")
    
@app.get("/find_type_by_type/",  tags = ["Type DAO"])
async def find_typ_typ(tx, nom):
    try:
        typ = TypeDao()
        return typ.find_type(Type(tx_remplissage= tx, nom= nom))
    except:
        raise Exception("Aucun type ne correspond")
    
@app.get("/find_id_type/",  tags = ["Type DAO"])
async def find_id_typ(tx, nom):
    try :
        typ = TypeDao() 
        return typ.find_id_type(Type(tx,nom))
    except:
        raise Exception("Aucun type ne correspond")

@app.put("/update_type_by_id/", tags = ["Type DAO"])
async def update_typ(id, new_tx_remplissage, new_nom):
   typ = TypeDao()
   typ.update_type_by_id(id, Type(new_tx_remplissage, new_nom))

@app.delete("/delete_type_by_id/", tags = ["Type DAO"])
async def delete_typ(id) :
    try :
        typ = TypeDao()
        typ.delete_type_by_id(id)
    except:
        raise Exception("Aucun type ne correspond à cet id")

@app.delete("/delete_type_by_type/",  tags = ["Type DAO"])
async def delete_typ_typ(nom, tx_remplissage,) :
    typ = TypeDao()
    typ.delete_type(Type(tx_remplissage, nom))

@app.delete("/delete_all_type/", tags = ["Type DAO"])
async def delete_all_mod():
    typ = TypeDao()
    typ.delete_all_type()

@app.get("/find_all_meta/", tags = ["Metatype DAO"])
async def find_metas():
    met = MetaDao()
    return met.find_all_meta()

@app.get("/find_ids_meta/",  tags = ["Metatype DAO"])
async def find_ids_met(nom_m):
    try :
        met = MetaDao()
        return met.find_ids_meta(nom_m)
    except:
        raise Exception("Aucun méta_type ne correspond à cet id")

@app.get("/find_meta_by_name/",  tags = ["Metatype DAO"])
async def find_meta_name(nom_meta):
    try :
        met = MetaDao()
        return met.find_meta_by_name(nom_meta)
    except:
        raise Exception("Aucun meta_type ne correspond")

@app.delete("/delete_meta_by_name/", tags = ["Metatype DAO"])
async def delete_meta_name(nom_meta):
    met = MetaDao()
    met.delete_meta_by_name(nom_meta)

@app.delete("/delete_all_meta_type/", tags = ["Metatype DAO"])
async def delete_all_mod():
    met = MetaDao()
    met.delete_all_meta_type()

@app.get("/find_all_data/",  tags = ["Donnees DAO"])
async def find_datas():
    dat = DataDao()
    return dat.find_all_data()

@app.get("/find_data_by_id/",  tags = ["Donnees DAO"])
async def find_dat_id(id : int):
    try :
        dat = DataDao()
        return dat.find_data_by_id(id)
    except:
        raise Exception("Aucune donnée ne correspond à cet id")

@app.get("/find_data_by_meta/", tags = ["Donnees DAO"])
async def find_dat_meta(nom_meta):
    dat = DataDao()
    return dat.find_data_by_meta(nom_meta)

@app.get("/find_row_data/",  tags = ["Donnees DAO"])
async def find_row_dat(nom_meta, nb_row):
    n_row = int(nb_row)
    if n_row <=  Generation_donnee.tailles[Generation_donnee.meta_type1.index(nom_meta)]:
        dat = DataDao()
        return dat.find_row_data(nom_meta, n_row, len(Meta_type.dict_meta_type[nom_meta]))
    else :
        raise Exception("Veuillez entrer un numéro de ligne inférieur à nombre total de lignes généré")

@app.get("/find_col_data/", tags = ["Donnees DAO"])
async def find_col_dat(nom_meta, nom_col):
    try :
        dat = DataDao()
        return dat.find_col_data(nom_meta, nom_col)
    except :
        raise Exception("Veuillez entrer un nom de colonne existant pour le métatype considéré")
    
@app.get("/find_id_donnee/", tags = ["Donnees DAO"])
async def find_id_dat(nom_meta, nom_type, ordre, valeur) :
    dat = DataDao()
    dat.find_id_donnee([nom_meta, nom_type, ordre, valeur])

@app.put("/update_data_by_id/", tags = ["Donnees DAO"])
async def update_data(id, nom_meta, nom_type, ordre, valeur):
    try : 
        dat = DataDao()
        dat.update_data_by_id(id, [nom_meta, nom_type, ordre, valeur])
    except:
        raise Exception("Aucune donnée ne correspond à cet id")

@app.delete("/delete_row_data/", tags = ["Donnees DAO"])
async def delete_row(nom_meta, i_row) :
    n_row = int(i_row)
    if n_row <=  Generation_donnee.tailles[Generation_donnee.meta_type1.index(nom_meta)] :
        dat = DataDao()
        dat.delete_row_data(nom_meta, len(Meta_type.dict_meta_type[nom_meta]), n_row)
    else :
        raise Exception("Veuillez entrer un numéro de ligne inférieur à nombre total de lignes généré")

@app.delete("/delete_data_by_id/",  tags = ["Donnees DAO"])
async def delete_dat_id(id) :
    dat = DataDao()
    dat.delete_data_by_id(id)

@app.delete("/delete_data_by_meta/", tags = ["Donnees DAO"])
async def delete_dat_meta(nom_meta):
    try:
        dat = DataDao()
        dat.delete_data_by_meta(nom_meta)
    except:
        raise Exception("Le méta-type n'est pas présent dans la table")

@app.delete("/delete_all_data/",  tags = ["Donnees DAO"])
async def delete_all_data():
    dat = DataDao()
    dat.delete_all_data()




    




if __name__ == "__main__":
    uvicorn.run(app, host = "127.0.0.1", port = 8000)