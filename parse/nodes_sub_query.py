from abc import abstractmethod
from pypika.terms import BasicCriterion, ComplexCriterion, ValueWrapper
from pypika import Query, Table
from config import nested_conditon_mapping, equality_mapping, \
    order_mapping, func_mapping


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

    def __init__(self, name, node_type, transform_json, query=None):
        super(InputNode, self).__int__(name, node_type, transform_json, query=query)

    def transformObject(self):
        """
        List the columns to be selected for the query.
        :return:
        """
        column_list = self.transform_json["fields"]
        table = Table(self.transform_json["tableName"])
        self.query = Query.from_(table).select(*column_list)
        return self.query

class FilterNode(Nodes):

    def __init__(self, node, graph_order, query=None):
        super(FilterNode, self).__int__(node, graph_order, query=query)

    def transformObject(self):

        table = self.query
        column_list = list(map(lambda x: x.name, self.query._selects))
        column = self.transform_json["variable_field_name"]
        joinoperator = self.transform_json["joinOperator"]
        operations = self.transform_json["operations"]
        conditions=[]
        for condition in operations:
            operator = condition["operator"]
            value = condition["value"]
            conditions+= [BasicCriterion(equality_mapping[operator],
                                        table.field(column),
                                        ValueWrapper(value)) ]
        where_conditon = conditions
        if len(conditions)>1:
            where_conditon = [ComplexCriterion(nested_conditon_mapping[joinoperator], *conditions)]
        query = Query.from_(table).select(*column_list).where(*where_conditon)
        return query

class SortNode(Nodes):

    def __init__(self, name, node_type, transform_json, query=None):
        super(SortNode, self).__int__(name, node_type, transform_json, query=query)

    def transformObject(self):
        table = self.query
        column_list = self.query._selects
        column_list = list(map(lambda x: x.name, column_list))
        order_column = list(map(lambda x: x["target"], self.transform_json))
        order_direction = list(map(lambda x: x["order"], self.transform_json))
        column_order = list(zip(order_column, order_direction))
        query = Query.from_(table).select(*column_list)
        for column, order in column_order:
            query = query.orderby(column, order_mapping[order.lower()])

        return query


class TextTransformationNode(Nodes):

    def __init__(self, name, node_type, transform_json, query=None):
        super(TextTransformationNode, self).__int__(name, node_type, transform_json, query=query)

    def transformObject(self):
        table = self.query
        column_list = self.query._selects
        column_list = list(map(lambda x: x.name, column_list))

        query = Query.from_(table).select(*column_list)
        new_column_list = query._selects
        for val in self.transform_json:
            column, transformation  = val["column"], val["transformation"].lower()
            query._selects = [func_mapping[transformation](col, alias=column)
                               if col.name == column else col for col in new_column_list]

        return query

class OutputNode(Nodes):

    def __init__(self, name, node_type, transform_json, query=None):
        super(OutputNode, self).__int__(name, node_type, transform_json, query=query)

    def transformObject(self):
        table = self.query
        limit, offset = self.transform_json['limit'], self.transform_json['offset']
        query = Query.from_(table).select('*')[offset:limit]
        return query

class QueryFactory:
    def get_query(self, name, node_type, transform_json, query=None):
        if node_type == "INPUT":
            return InputNode(name, node_type, transform_json, query).transformObject()

        elif node_type == "FILTER":
            return FilterNode(name, node_type, transform_json, query).transformObject()

        elif node_type == "SORT":
            return SortNode(name, node_type, transform_json, query).transformObject()

        elif node_type == "TEXT_TRANSFORMATION":
                return TextTransformationNode(name, node_type, transform_json, query).transformObject()

        elif node_type == "OUTPUT":
            return OutputNode(name, node_type, transform_json, query).transformObject()