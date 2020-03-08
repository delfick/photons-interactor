describe("Dashboard", () => {
  it("Does not do much!", () => {
    cy.visit("/");
    cy.get("[data-cy=bulb]").should("have.length", 7);
    cy.get("[data-cy=bulb-label]").should("have.length", 7);
  });
});
