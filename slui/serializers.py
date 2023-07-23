from rest_framework import serializers
from slfrase.models import TextPair, StudyState


class StudyingSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    question = serializers.CharField(read_only=True)
    possible_answers = serializers.CharField(read_only=True)
    answer = serializers.CharField(allow_null=False, write_only=True)
    is_passed_flg = serializers.BooleanField(read_only=True)

    class Meta:
        model = StudyState
        fields = ("id", "question", "possible_answers", "answer", "is_passed_flg")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance: StudyState = self.instance
        answer = attrs["answer"]

        answer = TextPair.get_words(answer.lower())
        variants = [TextPair.get_words(x.lower())
                    for x in TextPair.get_text_list(instance.possible_answers)]

        attrs["is_passed_flg"] = answer in variants
        return attrs

    def create(self):
        raise NotImplementedError

    def update(self, instance, validated_data):
        instance.is_passed_flg = validated_data["is_passed_flg"]
        instance.save()
        return instance


