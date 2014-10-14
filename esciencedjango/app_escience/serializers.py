from rest_framework import serializers
from app_escience.models import UserInfo
from app_escience.models import ClusterInfo


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    
    cluster = serializers.SerializerMethodField('number_of_clusters')
    class Meta:
        model = UserInfo
        fields = ('user_id', 'cluster')
        
        
    def number_of_clusters(self, obj):

        clusters = ClusterInfo.objects.all().filter(user_id = obj.user_id).filter(cluster_status = 1).count()
        return clusters

