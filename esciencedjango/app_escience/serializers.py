from rest_framework import serializers
from app_escience.models import UserInfo
from app_escience.models import ClusterInfo


class OkeanosTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    
    cluster = serializers.SerializerMethodField('number_of_clusters')
    escience_token = serializers.RelatedField()
    class Meta:
        model = UserInfo
        fields = ('user_id', 'cluster', 'escience_token')
        
        
    def number_of_clusters(self, obj):

        clusters = ClusterInfo.objects.all().filter(user_id = obj.user_id).filter(cluster_status = 1).count()
        return clusters

