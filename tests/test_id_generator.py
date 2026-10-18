from app.ids.generator import IdGenerator


def test_generated_ids_increase() -> None:
    generator = IdGenerator(1)

    first = generator.generate()
    second = generator.generate()

    assert second > first
