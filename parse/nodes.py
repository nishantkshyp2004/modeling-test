from abc import abstractmethod
from pypika.terms import BasicCriterion, ComplexCriterion, ValueWrapper
from pypika import Query, Table
from config import nested_conditon_mapping, equality_mapping, \
    order_mapping, func_mapping

class GraphStructure:
    def __init__(self, file_name):
        self.json  = open(file_name).read()

class Nodes:

    def __int__(self, node, graph_order, query=None):
        self.name = node["key"]
        self.type = node["type"]
        self.transform_json = node["transformObject"]
        self.query = query
        self.graph_order = graph_order

    def __str__(self):
        return self.name

    @abstractmethod
    def transformObject(self):
        pass

class InputNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        super(InputNode, self).__int__( node, graph_order, query=query)

    def transformObject(self):
        """
        List the columns to be selected for the query.
        :return: QueryBuilder object
        """
        column_list = self.transform_json["fields"]
        table = Table(self.transform_json["tableName"])
        self.query = Query.from_(table).select(*column_list)
        return self.query

class FilterNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        """
        Initialize the Node paramters and get the predecessor node name.
        :param node: node dict
        :param graph_order: graph nodes ordered list.
        :param query: None or previous query to generate new subquery.
        """
        super(FilterNode, self).__int__( node, graph_order, query=query)
        self.predecessor_node_name = self.graph_order[self.graph_order.index(self.name)-1]

    def transformObject(self):
        """
        Generating filter query using where clause.
        :return: QueryBuilder object
        """
        query = self.query
        #List all columns from the query.
        column_list = list(map(lambda x: x.name, self.query._selects))
        column = self.transform_json["variable_field_name"]
        joinoperator = self.transform_json["joinOperator"]
        operations = self.transform_json["operations"]
        where_condition=[]
        #Handling multiple operations, listed in request-json.
        for condition in operations:
            operator, value  = condition["operator"], condition["value"]
            query.field(column).table.alias = "A"
            where_condition+= [BasicCriterion(equality_mapping[operator], query.field(column),
                                              ValueWrapper(value))]

        #If conditions are more than 1 then generate the complex criterion query.
        if len(where_condition)>1:
            where_condition = [ComplexCriterion(nested_conditon_mapping[joinoperator.lower()], *where_condition)]
        #Generating the with clause for sub query.
        query = Query.from_(query).select(*column_list).where(*where_condition)
        return query

class SortNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        """
        Initialize the Node paramters and get the predecessor node name.
        :param node: node dict
        :param graph_order: graph nodes ordered list.
        :param query: None or previous query to generate new subquery.
        """
        super(SortNode, self).__int__( node, graph_order, query=query)
        self.predecessor_node_name = self.graph_order[self.graph_order.index(self.name)-1]

    def transformObject(self):
        """
        Generating sort query using orderby clause.
        :return: QueryBuilder object
        """
        query = self.query

        column_list = list(map(lambda x: x.name, self.query._selects))
        #Collect all target columns, and their orders.
        order_column = list(map(lambda x: x["target"], self.transform_json))
        order_direction = list(map(lambda x: x["order"], self.transform_json))
        #Zipping all target(columns) and order together.
        column_order = list(zip(order_column, order_direction))
        #Generate query using with clause.
        query = Query.from_(query).select(*column_list)
        # generate orderby clause using column_order.
        for column, order in column_order:
            query = query.orderby(column, order_mapping[order.lower()])

        return query


class TextTransformationNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        """
        Initialize the Text Tranformation Node paramters and get the predecessor node name.
        :param node: node dict
        :param graph_order: graph nodes ordered list.
        :param query: None or previous query to generate new subquery.
        """
        super(TextTransformationNode, self).__int__( node, graph_order, query=query)
        self.predecessor_node_name = self.graph_order[self.graph_order.index(self.name)-1]

    def transformObject(self):
        """
        Generate query with the text transformation.
        :return: QueryBuilder object
        """
        query = self.query
        column_list = list(map(lambda x: x.name, self.query._selects))
        query = Query.from_(query).select(*column_list)
        new_column_list = query._selects
        for val in self.transform_json:
            column, transformation = val["column"], val["transformation"].lower()
            query._selects = [func_mapping[transformation](col, alias=column)
                              if col.name == column else col for col in new_column_list]

        return query

class OutputNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        """
        Initialize the Output Node parameters and get the predecessor node name.
        :param node: node dict
        :param graph_order: graph nodes ordered list.
        :param query: None or previous query to generate new subquery.
        """
        super(OutputNode, self).__int__( node, graph_order, query=query)
        self.predecessor_node_name = self.graph_order[self.graph_order.index(self.name)-1]

    def transformObject(self):
        """
        Generate query using limit and offset.
        :return: QueryBuilder object
        """
        query = self.query
        #Generate query using with clause for predecessor node.
        limit, offset = self.transform_json['limit'], self.transform_json['offset']
        #Generate query using with clause for current node.
        query = Query.from_(query).select('*')[offset:limit]
        return query


class QueryFactory:
    """
    Query Factory to generate query required using different creteria.
    """
    def get_query(self, node, graph_order, query=None):
        """
        Get final generate sql query.
        :param node: Node Dict
        :param graph_order: graph nodes ordered list.
        :param query: None or previous query to generate new subquery.
        :return: QueryBuilder
        """
        if node["type"] == "INPUT":
            return InputNode(node, graph_order, query).transformObject()

        elif node["type"] == "FILTER":
            return FilterNode(node, graph_order, query).transformObject()

        elif node["type"] == "SORT":
            return SortNode(node, graph_order, query).transformObject()

        elif node["type"] == "TEXT_TRANSFORMATION":
            return TextTransformationNode(node, graph_order, query).transformObject()

        elif node["type"] == "OUTPUT":
            return OutputNode(node, graph_order, query).transformObject()





