from django.db import connection

from common import BaseEvolutionOperations

class EvolutionOperations(BaseEvolutionOperations):
    def add_column(self, model, f, initial):
        qn = connection.ops.quote_name
    
        if f.rel:
            # it is a foreign key field
            # NOT NULL REFERENCES "django_evolution_addbasemodel" ("id") DEFERRABLE INITIALLY DEFERRED
            # ALTER TABLE <tablename> ADD COLUMN <column name> NULL REFERENCES <tablename1> ("<colname>") DEFERRABLE INITIALLY DEFERRED
            related_model = f.rel.to
            related_table = related_model._meta.db_table
            related_pk_col = related_model._meta.pk.name
            constraints = ['%sNULL' % (not f.null and 'NOT ' or '')]
            if f.unique or f.primary_key:
                constraints.append('UNIQUE')
            params = (qn(model._meta.db_table), qn(f.column), f.db_type(), ' '.join(constraints), 
                qn(related_table), qn(related_pk_col), connection.ops.deferrable_sql())
            output = ['ALTER TABLE %s ADD COLUMN %s %s %s REFERENCES %s (%s) %s;' % params]
        else:
            null_constraints = '%sNULL' % (not f.null and 'NOT ' or '')
            if f.unique or f.primary_key:
                unique_constraints = 'UNIQUE'
            else:
                unique_constraints = ''

            # At this point, initial can only be None if null=True, otherwise it is 
            # a user callable or the default AddFieldInitialCallback which will shortly raise an exception.
            if initial is not None:
                if callable(initial):
                    initial_value = initial()
                else:
                    initial_value = initial

                params = {
                        'table': qn(model._meta.db_table),
                        'column': qn(f.column),
                        'db_type': f.db_type(),
                        'unique_constraints': unique_constraints,
                        'null_constraints': null_constraints,
                        'initial': initial_value,
                    }

                output = ["ALTER TABLE %(table)s ADD COLUMN %(column)s %(db_type)s %(unique_constraints)s %(null_constraints)s DEFAULT '%(initial)s';" % params]
            else:
                params = (qn(model._meta.db_table), qn(f.column), f.db_type(),' '.join([null_constraints, unique_constraints]))
                output = ['ALTER TABLE %s ADD COLUMN %s %s %s;' % params]        
        return output

    def rename_column(self, opts, old_field, new_field):
        if old_field.column == new_field.column:
            # No Operation
            return []
    
        qn = connection.ops.quote_name
        params = (qn(opts.db_table), qn(old_field.column), qn(new_field.column))
        return ['ALTER TABLE %s RENAME COLUMN %s TO %s;' % params]

