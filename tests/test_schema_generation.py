import pytest
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestSchemaGeneration:
    def test_schema_generation(self):
        """Test that the OpenAPI schema can be generated successfully."""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        assert schema is not None
        assert 'openapi' in schema
        assert 'paths' in schema
        assert 'components' in schema
        assert 'schemas' in schema['components']

    def test_csi300_schema_presence(self):
        """Test that CSI300 endpoints are present in the schema."""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        paths = schema['paths']
        
        # Verify core endpoints
        assert '/api/csi300/api/companies/' in paths
        assert '/api/csi300/api/companies/{id}/' in paths
        
        # Verify custom actions
        assert '/api/csi300/api/companies/filter_options/' in paths
        assert '/api/csi300/api/companies/search/' in paths
        assert '/api/csi300/api/companies/{id}/investment_summary/' in paths

    def test_filter_options_schema(self):
        """Test specific schema structure for filter_options."""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        
        path_item = schema['paths']['/api/csi300/api/companies/filter_options/']
        assert 'get' in path_item
        operation = path_item['get']
        
        # Check parameters
        parameters = operation.get('parameters', [])
        param_names = [p['name'] for p in parameters]
        assert 'region' in param_names
        assert 'im_sector' in param_names
        
        # Check response
        responses = operation['responses']
        assert '200' in responses

    def test_search_schema(self):
        """Test specific schema structure for search."""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        
        path_item = schema['paths']['/api/csi300/api/companies/search/']
        operation = path_item['get']
        
        # Check required parameter 'q'
        parameters = operation.get('parameters', [])
        q_param = next((p for p in parameters if p['name'] == 'q'), None)
        assert q_param is not None
        assert q_param.get('required') is True

    def test_company_schema_fields(self):
        """Test that the Company model fields are correctly exposed in the schema."""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        
        components = schema['components']['schemas']
        assert 'CSI300Company' in components
        company_schema = components['CSI300Company']
        properties = company_schema['properties']
        
        # Verify key financial fields
        assert 'market_cap_local' in properties
        assert 'market_cap_usd' in properties
        assert 'pe_ratio_trailing' in properties
        assert 'region' in properties
        assert 'im_sector' in properties

