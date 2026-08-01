"""Tests for The 511 camera platform."""

from __future__ import annotations

from homeassistant.components.camera import async_get_image
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME


async def _setup_entry(hass, fake_provider_class):
    """Set up a config entry for the fake provider and return it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


async def test_camera_entity_is_created(hass, fake_provider_class):
    """Setup should create a camera entity from the provider's camera data."""
    await _setup_entry(hass, fake_provider_class)

    state = hass.states.get("camera.the_511_test_camera")
    assert state is not None
    assert state.name == "The 511 Test Camera"
    assert state.attributes["road"] == "I-94"
    assert state.attributes["direction"] == "East"
    assert state.attributes["latitude"] == 43.0
    assert state.attributes["longitude"] == -89.0
    assert state.attributes["status"] == "Enabled"
    assert state.attributes["video_url"] == "https://example.com/cam-1.m3u8"


async def test_camera_entity_has_stable_unique_id(hass, fake_provider_class):
    """The camera entity should expose a provider-scoped unique id."""
    await _setup_entry(hass, fake_provider_class)

    entity = async_get_entity_registry(hass).async_get("camera.the_511_test_camera")

    assert entity is not None
    assert entity.unique_id == "fake-cam-1"


async def test_camera_fetches_image(hass, aioclient_mock, fake_provider_class):
    """Requesting a snapshot should fetch bytes from the camera image URL."""
    aioclient_mock.get(
        "https://example.com/cam-1.jpg",
        content=b"fake-image-bytes",
        headers={"Content-Type": "image/jpeg"},
    )
    await _setup_entry(hass, fake_provider_class)

    image = await async_get_image(hass, "camera.the_511_test_camera")

    assert image.content == b"fake-image-bytes"
