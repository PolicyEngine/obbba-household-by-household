import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import HouseholdProfile from './HouseholdProfile.svelte';

describe('HouseholdProfile scroll position', () => {
  let household1, household2;
  
  beforeEach(() => {
    household1 = {
      id: '1001',
      'State': 'CA',
      'Age of Head': 35,
      'Is Married': true,
      'Number of Dependents': 2,
      'Market Income': 75000,
      'Baseline Net Income': 65000,
      'Total Change in Net Income': 1500,
      'Percentage Change in Net Income': 2.3
    };
    
    household2 = {
      id: '2002',
      'State': 'NY',
      'Age of Head': 42,
      'Is Married': false,
      'Number of Dependents': 1,
      'Market Income': 95000,
      'Baseline Net Income': 80000,
      'Total Change in Net Income': -500,
      'Percentage Change in Net Income': -0.6
    };
  });

  it('should not move when household changes', async () => {
    const { container, rerender } = render(HouseholdProfile, {
      props: {
        household: household1,
        selectedDataset: 'tcja-expiration',
        onRandomize: vi.fn()
      }
    });

    // Get the household profile element
    const profileElement = container.querySelector('.household-profile');
    expect(profileElement).toBeTruthy();

    // Record initial position
    const initialRect = profileElement.getBoundingClientRect();
    const initialTop = initialRect.top;
    const initialLeft = initialRect.left;

    // Mock scrolling behavior
    const scrollSpy = vi.fn();
    window.addEventListener('scroll', scrollSpy);
    
    // Change to a different household
    await rerender({
      household: household2,
      selectedDataset: 'tcja-expiration',
      onRandomize: vi.fn()
    });

    // Wait for any animations or updates
    await tick();
    await new Promise(resolve => setTimeout(resolve, 100));

    // Check that no scroll occurred
    expect(scrollSpy).not.toHaveBeenCalled();

    // Check position hasn't changed (allowing for minor rounding differences)
    const newRect = profileElement.getBoundingClientRect();
    expect(Math.abs(newRect.top - initialTop)).toBeLessThan(1);
    expect(Math.abs(newRect.left - initialLeft)).toBeLessThan(1);

    window.removeEventListener('scroll', scrollSpy);
  });

  it('should not move when clicking shuffle button', async () => {
    const onRandomize = vi.fn();
    const { container, getByTitle } = render(HouseholdProfile, {
      props: {
        household: household1,
        selectedDataset: 'tcja-expiration',
        onRandomize
      }
    });

    const profileElement = container.querySelector('.household-profile');
    const initialRect = profileElement.getBoundingClientRect();

    // Mock scroll and focus behaviors
    const scrollSpy = vi.fn();
    window.addEventListener('scroll', scrollSpy);
    
    const preventDefaultSpy = vi.fn();
    const stopPropagationSpy = vi.fn();
    const blurSpy = vi.fn();

    // Click shuffle button
    const shuffleButton = getByTitle('Pick a new random household');
    
    // Override blur method to track it was called
    shuffleButton.blur = blurSpy;

    // Create a custom event with our spy methods
    const clickEvent = new MouseEvent('click', { 
      bubbles: true, 
      cancelable: true 
    });
    clickEvent.preventDefault = preventDefaultSpy;
    clickEvent.stopPropagation = stopPropagationSpy;

    fireEvent(shuffleButton, clickEvent);

    // Verify prevention methods were called
    expect(preventDefaultSpy).toHaveBeenCalled();
    expect(stopPropagationSpy).toHaveBeenCalled();
    expect(blurSpy).toHaveBeenCalled();
    expect(onRandomize).toHaveBeenCalled();

    // Verify no scroll occurred
    expect(scrollSpy).not.toHaveBeenCalled();

    // Check position hasn't changed
    await tick();
    const newRect = profileElement.getBoundingClientRect();
    expect(Math.abs(newRect.top - initialRect.top)).toBeLessThan(1);
    expect(Math.abs(newRect.left - initialRect.left)).toBeLessThan(1);

    window.removeEventListener('scroll', scrollSpy);
  });

  it('should have overflow-anchor: none CSS property', async () => {
    const { container } = render(HouseholdProfile, {
      props: {
        household: household1,
        selectedDataset: 'tcja-expiration',
        onRandomize: vi.fn()
      }
    });

    const profileElement = container.querySelector('.household-profile');
    const computedStyle = window.getComputedStyle(profileElement);
    
    // Note: This test might not work in jsdom as it doesn't fully support all CSS properties
    // But it documents the intent
    expect(profileElement.style.overflowAnchor || computedStyle.overflowAnchor).toBe('none');
  });
});