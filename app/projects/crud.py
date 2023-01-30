from datetime import datetime

from app.utils.db import get_neo4j_driver
from app.utils.schema import ProjectNode, ProjectNodeList, ProjectNodeProperties
from fastapi import APIRouter, HTTPException, status

router = APIRouter()
neo4j_driver = get_neo4j_driver()

node_labels = "Project"
base_properties = ["created_at"]
expected_properties = ["name", "description", "start_date", "end_date"]


@router.post("/", response_model=ProjectNode)
async def create_project(
    node_attributes: ProjectNodeProperties, label: str = node_labels
):
    # Check that attributes dictionary does not modify base fields
    node_attributes = node_attributes.dict()
    for key in node_attributes:
        if key in base_properties:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, {key} is a base property",
            )
        if key not in expected_properties:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, {key} is not a valid property",
            )

    unpacked_attributes = "SET " + ", ".join(
        f"new_node.{key}='{value}'" for (key, value) in node_attributes.items()
    )

    cypher = (
        f"CREATE (new_node:{label})\n"
        "SET new_node.created_at = $created_at\n"
        f"{unpacked_attributes}\n"
        "RETURN new_node, LABELS(new_node) as labels, ID(new_node) as id"
    )

    try:
        with neo4j_driver.session() as session:
            result = session.run(
                query=cypher,
                parameters={
                    "created_at": str(datetime.utcnow()),
                    "attributes": node_attributes,
                },
            )
            node_data = result.data()[0]

            return ProjectNode(
                node_id=node_data["id"],
                labels=node_data["labels"],
                properties=node_data["new_node"],
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating node: {e}",
        )


# search on projects by property
@router.get("/search", response_model=ProjectNodeList)
async def search_projects(search_node_property: str, node_property_value: str):
    cypher = (
        f"Match (node)\n"
        f"WHERE node.{search_node_property} = '{node_property_value}'\n"
        "RETURN ID(node) as id, LABELS(node) as labels, node"
    )

    try:
        with neo4j_driver.session() as session:
            result = session.run(query=cypher)

            collection_data = result.data()

        node_list = []
        for node in collection_data:
            node = ProjectNode(
                node_id=node["id"], labels=node["labels"], properties=node["node"]
            )
            node_list.append(node)

        return ProjectNodeList(nodes=node_list)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error getting nodes: {e}",
        )


# get all projects
@router.get("/", response_model=ProjectNodeList)
async def get_projects():
    cypher = f"Match (node:Project) RETURN ID(node) as id, LABELS(node) as labels, node"

    try:
        with neo4j_driver.session() as session:
            result = session.run(query=cypher)
            collection_data = result.data()

        node_list = []
        for node in collection_data:
            node = ProjectNode(
                node_id=node["id"], labels=node["labels"], properties=node["node"]
            )
            node_list.append(node)

        return ProjectNodeList(nodes=node_list)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error getting nodes: {e}",
        )


# get a single projects
@router.get("/{node_id}", response_model=ProjectNode)
async def get_project(node_id: int):
    cypher = f"match (node:Project) where id(node)={node_id} RETURN ID(node) as id, LABELS(node) as labels, node"

    try:
        with neo4j_driver.session() as session:
            result = session.run(query=cypher)
            node_data = result.data()[0]

        return ProjectNode(
            node_id=node_data["id"],
            labels=node_data["labels"],
            properties=node_data["node"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error getting node: {e}",
        )


# get a single projects
@router.delete("/{node_id}")
async def delete_project(node_id: int):
    cypher = f"match (node:Project) where id(node)={node_id} DETACH DELETE node"

    try:
        with neo4j_driver.session() as session:
            result = session.run(query=cypher)
            node_data = result.data()

        if not node_data:
            return {"response": f"Node with ID: {node_id} was successfully deleted."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting node: {e}",
        )
