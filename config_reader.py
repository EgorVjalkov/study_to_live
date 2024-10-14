from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


host = '85.193.80.126'
user = 'egorok'
db_name = 'study_to_live'


class Settings(BaseSettings):
    admin_id: SecretStr
    test_token: SecretStr
    work_token: SecretStr
    db_password: SecretStr

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    def get_token(self, mode: str = ''):
        if mode == 'test':
            return self.test_token.get_secret_value()
        else:
            return self.work_token.get_secret_value()

    def get_admin_id(self):
        return int(self.admin_id.get_secret_value())

    def get_connection_str(self):
        connection_data = [user, self.db_password.get_secret_value(), host, db_name]
        return '{0}:{1}@{2}:5432/{3}'.format(*connection_data)


config = Settings()
