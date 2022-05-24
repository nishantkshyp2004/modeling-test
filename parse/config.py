from pypika import Order
from pypika.enums import Equality, Boolean
from pypika.terms import Criterion
import pypika.functions as func
equality_mapping = {"=":Equality.eq,
                    ">":Equality.gt,
                    "<":Equality.lt,
                    ">=":Equality.gte,
                    "<=":Equality.lte,
                    "<>":Equality.ne}

super_condition_mapping = {"and": Criterion.all,
                           "or": Criterion.any
                           }

nested_conditon_mapping = {
    "and":Boolean.and_,
    "or":Boolean.or_
}

order_mapping = {"desc": Order.desc,
                 "asc":Order.asc}

func_mapping = {"concat":func.Concat,
                "lower":func.Lower,
                "upper":func.Upper,
                "reverse":func.Reverse,
                "trim":func.Trim,
                "replace":func.Replace
}